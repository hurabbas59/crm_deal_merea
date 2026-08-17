class ExcelService:
    """Excel import/export adapter placeholder.

    The current workbook schema comes from Kalkulation.xlsx:
    Pipeline, Parzellen, and Baunebenkosten.
    """

    def import_workbook(self, path: str) -> None:
        raise NotImplementedError(f"Excel import not implemented yet: {path}")

    def export_workbook(self, path: str) -> None:
        raise NotImplementedError(f"Excel export not implemented yet: {path}")

