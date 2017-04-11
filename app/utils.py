import os
import re
import markdown2

def make_directory_tree(path):
    if not os.path.exists(path):
        make_directory_tree(os.path.dirname(path))
        try:
            os.mkdir(path)
        except FileExistsError as e:
            pass

def form_to_dict(form):
    output = {}
    for key in form:
        values = form.getlist(key)

        search = re.search(r'\[(\w+)\]', key)
        if search:
            sub_key = search.group(1)
            key = key.replace(search.group(0), '')
            if key not in output:
                output[key] = {}
            container = output[key]
            key_to_use = sub_key
        else:
            container = output
            key_to_use = key

        if len(values) == 1:
            container[key_to_use] = values[0]
        else:
            container[key_to_use] = values

    return output

def html_from_markdown(md_text):
    parsed_html = markdown2.markdown(md_text.encode("ascii", "xmlcharrefreplace"), extras=["fenced-code-blocks", "smarty-pants", "header-ids", "cuddled-lists", "tables"])
    return u"{}".format(parsed_html)
