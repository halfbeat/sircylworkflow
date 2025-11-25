import os


class Secrets(object):
    """
    Facilitates the usage of secrets, by parsing all files into
    an digestible object, without ever them touching the environment,
    which would be bad because they might be stored in docker layers, or
    accessed by other linked containers. All secret keys are transformed
    into snake case upper case.

    # If there's a file in /run/secrets/secret-key, their contents will be
    # accessible like so:
    secrets = Secrets()
    super_secret = secrets('SECRET_KEY')
    """

    BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')
    CUSTOM_SECRETS = {}

    def file_name_to_variable_name(self, name):
        """
        Turns a file name like 'file-name` to FILE_NAME
        """
        return name.replace(" ", "_").replace("-", "_").upper()

    def __init__(
            self,
            secrets_path="/run/secrets/",
            fallback_to_env=False,
            environ_object=None
    ) -> None:
        if environ_object is None:
            self.environ_object = os.environ
        else:
            self.environ_object = environ_object

        self.fallback_to_env = fallback_to_env

        if os.path.exists(secrets_path):
            secrets = os.listdir(secrets_path)
        else:
            secrets = []
        for secret_file_name in secrets:
            full_secret_file_path = os.path.join(
                secrets_path,
                secret_file_name
            )
            if os.path.isfile(full_secret_file_path):
                with open(full_secret_file_path) as secret_file:
                    key = self.file_name_to_variable_name(secret_file_name)
                    self.CUSTOM_SECRETS[key] = secret_file.read()

    def __call__(self, var, cast=None, default=None):
        return self.get_value(
            var, cast, default
        )

    def get_value(self, var, cast=None, default=None):
        if var in self.CUSTOM_SECRETS:
            value = self.CUSTOM_SECRETS[var]
        elif self.fallback_to_env:
            value = self.environ_object.get(var)
        else:
            value = default

        if cast is not None:
            value = self.parse_value(value, cast)
        return value

    @classmethod
    def parse_value(cls, value, cast):
        if cast is None:
            return value
        elif cast is bool:
            try:
                value = int(value) != 0
            except ValueError:
                value = value.lower() in cls.BOOLEAN_TRUE_STRINGS
            return value
