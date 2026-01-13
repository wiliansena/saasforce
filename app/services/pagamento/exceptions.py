class PagamentoError(Exception):
    pass


class PagamentoConfigNotFound(PagamentoError):
    pass


class PagamentoRequestError(PagamentoError):
    pass
