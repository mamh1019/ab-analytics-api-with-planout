# -*- coding: utf-8 -*-

class Query:
    @staticmethod
    def build_insert_statement(
        table, columns: list, dup_update_columns: list = [], ignore=False
    ):
        builders = ["INSERT"]
        if ignore is True and len(dup_update_columns) <= 0:
            builders.append("IGNORE")
        builders.append("INTO")
        builders.append(table)

        values = []
        params = []
        for col in columns:
            values.append(f"`{col}`")
            params.append(f":{col}")
        builders.append("(" + ",".join(values) + ") VALUES")
        builders.append("(" + ",".join(params) + ")")

        dup_cols = []
        if dup_update_columns is not None and len(dup_update_columns) > 0:
            for col in dup_update_columns:
                dup_cols.append(f"`{col}` = VALUES(`{col}`)")
            builders.append("ON DUPLICATE KEY UPDATE {}".format(",".join(dup_cols)))

        return " ".join(builders)

    @staticmethod
    def build_update_statement(table, columns: list, where_colums: list):
        builders = [f"UPDATE `{table}` SET"]

        set_cols = []
        for col in columns:
            set_cols.append(f"`{col}` = :{col}")

        where_cols = []
        for col in where_colums:
            where_cols.append(f"`{col}` = :{col}")

        builders.append(",".join(set_cols))
        builders.append("WHERE")
        builders.append(" AND ".join(where_cols))

        return " ".join(builders)
