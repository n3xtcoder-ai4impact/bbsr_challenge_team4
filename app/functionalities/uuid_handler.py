import pandas as pd
from app.model.RouterModels import MaterialMatchOut
from loguru import logger

def uuid_input_handler(uuid_input: str,
                       obd: pd.DataFrame,
                       specific_generic_mapping: pd.DataFrame) -> MaterialMatchOut:
    """Checks if a user input uuid is in OBD and decides how to proceed with it."""

    logger.info(f'user input: "{uuid_input}"')
    # Try to find the specific material in OBD
    specific_row = obd[obd['UUID'] == uuid_input]
    if specific_row.empty:
        message = f'Could not find UUID in Ökobaudat data.'
        return MaterialMatchOut(specific_material=None, matches=[], message=message)

    spec_row = specific_row.iloc[0].to_dict()
    import math
    def clean_name(val):
        if val is None:
            return None
        if isinstance(val, float) and math.isnan(val):
            return None
        if isinstance(val, str) and val.strip().lower() == 'nan':
            return None
        return val
    spec_name = (
        clean_name(spec_row.get('Name')) or
        clean_name(spec_row.get('Name (en)')) or
        clean_name(spec_row.get('Name (de)')) or
        clean_name(spec_row.get('Specific_Name')) or
        clean_name(spec_row.get('Generic_Name')) or
        'Unknown Material'
    )
    def extract_selected_attributes(row):
        import math
        density = row.get('Rohdichte (kg/m3)', row.get('Density', None))
        thickness = row.get('Schichtdicke (m)', row.get('Thickness', None))
        category = row.get('Kategorie (original)') or row.get('Kategorie (en)') or None
        def clean_nan(val):
            if val is None:
                return None
            if isinstance(val, float) and math.isnan(val):
                return None
            if isinstance(val, str) and val.strip().lower() == 'nan':
                return None
            return val
        return {
            'Category': category,
            'Density': clean_nan(density),
            'Thickness': clean_nan(thickness)
        }
    spec_attributes = extract_selected_attributes(spec_row)
    specific_material = {
        'uuid': uuid_input,
        'name': spec_name,
        'attributes': spec_attributes
    }

    matches_df = specific_generic_mapping[specific_generic_mapping['Specific_UUID'] == uuid_input]
    matches = []
    if matches_df.empty:
        message = 'Could not find any generic materials that match the input uuid'
    else:
        message = 'Found generic materials that match input uuid'
        for _, row in matches_df.iterrows():
            generic_uuid = row['Generic_UUID']
            generic_row = obd[obd['UUID'] == generic_uuid]
            if not generic_row.empty:
                gen_row = generic_row.iloc[0].to_dict()
                generic_name = (
                    gen_row.get('Name') or
                    gen_row.get('Name (en)') or
                    gen_row.get('Name (de)') or
                    gen_row.get('Generic_Name') or
                    gen_row.get('Specific_Name') or
                    'Unknown'
                )
            else:
                generic_name = row.get('Generic_Name', 'Unknown')
            score = row['Final_Score']
            generic_row = obd[obd['UUID'] == generic_uuid]
            if not generic_row.empty:
                gen_row = generic_row.iloc[0].to_dict()
                gen_attributes = extract_selected_attributes(gen_row)
            else:
                gen_attributes = {'Composition': None, 'Density': None, 'Thickness': None}
            matches.append({
                'uuid': generic_uuid,
                'name': generic_name,
                'attributes': gen_attributes,
                'score': score
            })

    return MaterialMatchOut(specific_material=specific_material, matches=matches, message=message)