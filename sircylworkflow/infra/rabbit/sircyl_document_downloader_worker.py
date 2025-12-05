import io
import json
import logging
import zipfile

from sircylclient.client import SircylClient, Asiento
from sircylclient.utils import slugify

from rabbitmq import RabbitMQWorker, RabbitMQ
from symetrickey import SymmetricKey
from viewmodel import AsientoViewDto


class SircylDocumentDownloaderWorker(RabbitMQWorker):
    def __init__(self, rabbit: RabbitMQ, queue_name: str, sircyl_client: SircylClient, output_exchange_name: str,
                 symmetric_key_instance: SymmetricKey):
        super().__init__(rabbit, queue_name)
        self.sircyl_client = sircyl_client
        self.output_exchange_name = output_exchange_name
        self.symmetric_key_instance = symmetric_key_instance

    def process_message(self, ch, method, properties, body):
        username = self.symmetric_key_instance.decrypt(properties.headers.get("usuario_sircyl"))
        password = self.symmetric_key_instance.decrypt(properties.headers.get("password_sircyl"))
        with self.sircyl_client.with_credentials(username, password):
            asiento = AsientoViewDto(**json.loads(body))
            id_plan = properties.headers.get("plan_id", "UNKNOWN_PLAN_ID")
            str_fregistro = asiento.fecha_registro.strftime("%Y%m%d")
            materia = slugify(asiento.materia, max_size=50)
            logging.info(
                f"Descargando la documentación del asiento {asiento.id}: {asiento.numero_registro} {asiento.materia}")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                asiento_d = Asiento(asiento.id, asiento.fecha_distribucion, asiento.materia, asiento.fecha_registro,
                                    asiento.numero_registro, asiento.origen, asiento.destino, asiento.estado,
                                    asiento.fecha_estado)
                for asiento, documento, error in self.sircyl_client.idocsasiento(asiento_d):
                    if error:
                        logging.error("Ha ocurrido un error al descargar un documento")
                        logging.error(error)
                    else:
                        file_name = slugify(documento.nombre)
                        zip_file.writestr(file_name, documento.contenido)
                headers = {
                    'plan_id': id_plan,
                    'fecha_registro': str_fregistro,
                    'numero_registro': asiento.numero_registro,
                    'file_name': f"{asiento.numero_registro}.zip",
                    'materia': materia,
                }
                self.rabbit.publish(self.output_exchange_name, f"sircyl.asientos.{asiento.numero_registro}.documentos",
                                    zip_buffer.getvalue(), headers)
                logging.info(
                    f"Se han descargado {len(zip_file.namelist())} documentos del asiento {asiento_d.id_asiento} y publicado en el exchange {self.output_exchange_name}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
