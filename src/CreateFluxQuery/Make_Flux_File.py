from CreateFluxQuery.Get_template_parameter import TemplateParameter
import string
import CreateFluxQuery.Parameter as p
import glob

class MakeFluxFile:
    def __init__(self) -> None:
        pass
  
    # 情報を集めて出力
    def make_flux_file(self, query_num: str,  template_parameter:TemplateParameter):
        template_path = glob.glob("**/Template", recursive=True)[0]

        with open(template_path, "r", encoding="utf-8") as f:
            temp_content = f.read()
            tmp = string.Template(temp_content)

            values = {
                "IMPORT_MATH":      p.IMPORT_MATH,
                "IMPORT_STRINGS":   p.IMPORT_STRINGS,
                "IMPORT_REGEXP":    p.IMPORT_REGEXP,
                "IMPORT_DATE":      p.IMPORT_DATE,
                "QUERY_NUM":        query_num,
                "QUERY_INFO":       template_parameter.query_info,
                "QUERY_ELEM":       template_parameter.query_elem,
                # base
                "BUCKET":           template_parameter.bucket,
                "FILE_NAME":        template_parameter.output_filename,
                "MEASUREMENT":      template_parameter.measurement,
                "START_UTC":        template_parameter.start_utc,
                "STOP_UTC":         template_parameter.stop_utc,
                "TAG_FILTERS":      template_parameter.tag_filter,
                "FIELD_FILTERS":    template_parameter.field_filter,
                "JST_RANGE_CLIP":   template_parameter.jst_range_clip,
                # child query
                "CHILD_QUERY":      template_parameter.child_query,
                "CHILD_QUERY_NAME": template_parameter.child_query_name,
                # pivoted
                "PIVOTED_ROWKEY":   template_parameter.pivoted_rowkey,
                # result
                "RESULT_GROUP":     template_parameter.result_group,
                "RESULT_SORT":      template_parameter.result_sort,
                # "RESULT_RENAME":    template_parameter.result_rename,
                # "RESULT_KEEP":      template_parameter.result_keep,   
                "RESULT_MAP":       template_parameter.result_map,
                "YIELD_NAME":       template_parameter.yield_name
            }         
            ret = tmp.safe_substitute(values)

        # with open(f"output/{template_parameter.output_filename}", mode="w", encoding="utf-8") as file:
        #     file.write(ret)
        
        return ret
            
    def exec_func(self, query_num: str, template_parameter:TemplateParameter):
        print(f"{p.TAB(1)}Make Flux File")
        return self.make_flux_file(query_num, template_parameter)