Files for testing TBaustoff unmapped products

Initiate_Test_Mapping_TBS_Products.py will create 2 dataframes: 
  Reference_results_mapped_TBS_products_with_OBD_genericUUIDs.csv is the reality, what was already mapped 
  Reference_results_UNmapped_TBS_products_with_OBD_genericUUIDs.csv is the mapped products that we unmapped to test our mapping methods on these products

Assess_Mapping_TBS_Products.py is using
  Reference_results_UNmapped_TBS_products_with_OBD_genericUUIDs.csv to perform the mapping 
    the mapping method can be changed : currently TF-IDF is in the code but it could be a pre-trained model instead, or a combination of different method; 
        ideally, it could call the matching method code set by @Anindita and/or @Minh 
and then compare the results of this mapping with:
  Reference_results_mapped_TBS_products_with_OBD_genericUUIDs.csv 

This should help assess and improve our semantic linking method of TBaustoff products with UUIDs in OBD datasets
