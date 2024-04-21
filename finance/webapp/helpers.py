import logging
import dash_mantine_components as dmc


def create_add_btn(_id: dict | str):
    return dmc.Button(
        "Tilføj", id=_id,
        size="xs", mt="5px", variant="outline"
    )


def handle_update(old_data, new_data, entries, grp_name):
    if old_data is None or new_data is None:
        return

    if len(new_data) < len(old_data):
        new_data_names = [x['id'] for x in new_data]
        for x in entries:
            if x.id not in new_data_names:
                entries.remove(x)
                logging.debug(f"Expense: Removed {x.name} ({grp_name})")
    else:
        for idx, (new_row, old_row) in enumerate(zip(new_data, old_data)):
            for key, val in new_row.items():
                if val != old_row[key]:
                    entry = entries[idx]
                    setattr(entry, key, type(old_row[key])(new_row[key]))
                    logging.debug(
                        f"Expense: Changed {key} from {old_row[key]} to {new_row[key]} in {entry.name} ({grp_name})")