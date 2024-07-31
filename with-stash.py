import datetime
import os
import random
from glide import GlideApi, TableColumn
import demo_helpers

if __name__ == "__main__":
    glide = GlideApi()
    
    # create table
    rows = demo_helpers.get_rows_with_suffix("I")
    glide.stash_rows(rows)
    
    rows = demo_helpers.get_rows_with_suffix("II")
    glide.stash_rows(rows)
    
    name = "Employees " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_id = glide.create_table(name, demo_helpers.columns())

    print(f"Created new table from Table ID: {table_id}")

    input("Press Enter to continue with overwriting the table or  Ctrl+C to exit...")

    rows = demo_helpers.get_rows_with_suffix("III")
    glide.stash_rows(rows)
    rows = demo_helpers.get_rows_with_suffix("IV")
    glide.stash_rows(rows)

    glide.overwrite_table(table_id, demo_helpers.columns())




    
