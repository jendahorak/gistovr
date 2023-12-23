import arcpy
import os


def export_multipatch(fc: str, out_dir: str, source_col: str, group_field: str = None, disable_materials: bool = True) -> None:
    """
    Export a 3D layer to a feature class.

    Parameters:
    - fc (str): The path to the input feature layer with 3D display properties defined.
    - out_dir (str): The directory where the output feature class will be saved.
    - group_field (str, optional): The input feature's text field that will be used to merge multiple input features into the same output feature. Defaults to None.
    - disable_materials (bool, optional): Specifies whether color and texture properties will be maintained when exporting a 3D layer to a multipatch feature class. Defaults to False.

    Returns:
    - None
    """

    # Define the output feature class path
    out_feature_class = os.path.join(out_dir, f'{fc}_{group_field}_mtp')

    # Create a feature layer from the feature class
    feature_layer = arcpy.MakeFeatureLayer_management(
        fc, f'{fc}_{group_field}_mtp')

    # Convert the 3D layer to a feature class
    arcpy.ddd.Layer3DToFeatureClass(
        feature_layer, out_feature_class, group_field, disable_materials)

    print(f'Exported multipatch feature class - {group_field}.')
    print()


def semantic_mapping(fc: str, map_field, color_flag: False) -> None:
    """
    Update colorCategory and colorValue fields in a feature class based on the specified map type.

    Parameters:
    - fc (str): The path to the input feature class.
    - map_type (str): The type of map ('thematic' or 'topo1').

    Returns:
    - None
    """

    mapping_options = {
        'strecha_kod_text': {
            'category': {
                1: 'sedlova',
                2: 'mansardova',
                3: 'plocha',
                4: 'pultova',
                5: 'stanova',
                6: 'valbova',
                7: 'jina',
            },
            'color': {
                1: '#66c2a5',
                2: '#fc8d62',
                3: '#8da0cb',
                4: '#e78ac3',
                5: '#a6d854',
                6: '#ffd92f',
                7: '#e5c494',
            },
            'source_col': 'STRECHA_KOD',
            'abvr': 'sk',
        },

        'plocha_kod_text': {
            'category': {
                1: 'svisla_stena',
                2: 'vodorovna_strecha',
                3: 'sikma_strecha',
                4: 'zakladova_deska'
            },
            'color': {
                1: '#FFFFFF',
                2: '#B2B2B2',
                3: '#DE6034',
                4: '#FFFFFF',
            },
            'source_col': 'PLOCHA_KOD',
            'abvr': 'pk'

        },

        'cast_objektu_kod_text': {
            'category1': {
                1: 'komín',
                2: 'věž',
                3: 'vikýř, střešní nástavba',
                4: 'výtahová šachta, klimatizační jednotka',
                5: 'hlavní část objektu',
            },
            'category': {
                1: 'komin',
                2: 'vez',
                3: 'stresni_nastavba',
                4: 'vytahy_klimatizace',
                5: 'hlavni_cast_objektu',
            },
            'color': {
                1: '#FC8D62',
                2: '#A6D854',
                3: '#8DA0CB',
                4: '#E78AC3',
                5: '#E1E1E1',
            },
            'source_col': 'CAST_OBJEKTU',
            'abvr': 'co'

        },

        # make it so that multiple options can be selected, based on what options are selected that number of columns will be added and remapped by category
        # mapping of color will be optional and run by color_flag, if true coresponding color will be added to the colorValue field
    }

    colorCategory = 'colorCategory'
    colorValue = 'colorValue'

    colorCategoryColumnName = f'{colorCategory}_{mapping_options[map_field]["abvr"]}'
    colorValueColumnName = f'{colorValue}_{mapping_options[map_field]["abvr"]}'

    if not mapping_options[map_field]:
        print('Specified map type is not in the configuration mappings, please extend the mappings or provide correct map type')
    else:
        print(f"Updating {map_field}.")

        if map_field not in [f.name for f in arcpy.ListFields(fc)]:
            arcpy.AddField_management(fc, colorCategoryColumnName, 'TEXT')
            arcpy.AddField_management(
                fc, colorValueColumnName, 'TEXT')
            print(f'{map_field} added to the feature class.')
        else:
            print(f'{map_field} already exists in the feature class.')

        if map_field in mapping_options:
            source_col = mapping_options[map_field]['source_col']
            # clr = mapping_options[map_field]['color']

            with arcpy.da.UpdateCursor(fc, [colorCategoryColumnName, source_col, colorValueColumnName]) as cursor:
                for row in cursor:
                    row[0] = mapping_options[map_field]['category'].get(
                        row[1], 'Undefined')
                    row[2] = mapping_options[map_field]['color'].get(
                        row[1], 'Undefined')

                    cursor.updateRow(row)

                print("Update completed.")
        else:
            print(
                'Specified map type is not in the configuration mappings, please extend the mappings')


# TODO - make this runnable for all locations from  std_etapy_transformer.py

def main(input_gdb: str, output_gdb: str) -> None:
    # how to get to the specific featureclass in the gdb
    arcpy.env.workspace = input_gdb
    map_fields = ['strecha_kod_text',
                  'plocha_kod_text', 'cast_objektu_kod_text']

    # this is very bad but i dont want to refactor the code
    source_cols = ['STRECHA_KOD', 'PLOCHA_KOD', 'CAST_OBJEKTU']

    print('ran')

    for fc in arcpy.ListFeatureClasses("", ""):
        print(fc)
        sc = 0
        for map_field in map_fields:
            semantic_mapping(fc, map_field, False)
            # export_multipatch(
            #     fc, output_gdb, source_cols[sc], group_field=map_field)
            sc += 1


if __name__ == "__main__":
    input_gdb = '...'
    output_gdb = '...'

    main(input_gdb, output_gdb)
