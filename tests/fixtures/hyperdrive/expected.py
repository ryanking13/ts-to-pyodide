class Hyperdrive:
    _binding: Any

    def __init__(self, binding: JsProxy) -> None:
        self._binding = binding

    @property
    def connection_string(self) -> str:
        return self._binding.connectionString

    @property
    def host(self) -> str:
        return self._binding.host

    @property
    def port(self) -> int | float:
        return self._binding.port

    @property
    def user(self) -> str:
        return self._binding.user

    @property
    def password(self) -> str:
        return self._binding.password

    @property
    def database(self) -> str:
        return self._binding.database

    def connect(self) -> Any:
        return self._binding.connect()
