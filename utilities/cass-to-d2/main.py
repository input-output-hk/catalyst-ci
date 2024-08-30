import sys
import os
import re

class Table:
    def __init__(self) -> None:
        self.name = ""
        self.desc = ""
        self.fields: list[Field] = []
        self.pk: list[str] = []

    def to_d2_format(self) -> str:
        f_fields = []
        for field in self.fields:
          if field.is_only_comment():
              continue

          constraint_keys: list[str] = []

          if field.name in self.pk:
              constraint_keys.append("P")

          f_fields.append(field.to_d2_format(constraint_keys))

        return "\n".join([
            self.name + ": {",
            "\n".join(f_fields),
            "}"
        ])

class Field:
    def __init__(self) -> None:
        self.name = ""
        self.type = ""
        self.comment = ""

    def is_only_comment(self):
        return self.name == "" or self.type == ""
    
    def to_d2_format(self, constraint_keys: str) -> str:
        f_constraints = " {constraint: " + ", ".join(constraint_keys) + "}" if len(constraint_keys) else ""

        return "\t\t" + self.name + f": ({self.type})" + f_constraints

def extract_src(src_dir: str) -> list[Table]:
    if not os.path.isdir(src_dir):
        raise Exception(f"'{src_dir}' is not directory.")
    
    # get the list of files in the directory
    files = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

    return list(map(extract_file, files))

def extract_file(file_path: str) -> Table:
    f = open(file_path, "r")
    lines = f.readlines()

    table = Table()

    for line in lines:
        if line.strip() == "":
            continue
        
        # table description
        if table.name == "" and line.startswith("--"):
            table.desc += table.desc + ("" if table.desc == "" else " ") + line[2:].strip()
        # table name
        elif table.name == "" and "CREATE TABLE" in line:
            tokens = [x for x in re.split(r"\s+", line) if x]
            table.name = tokens[-2]
        # table fields
        elif table.name != "" and not line.startswith(")"):
            tokens = re.split(r"\s+", line.strip())

            if len(tokens) == 0:
                continue

            if tokens[0] == "PRIMARY":
                matches = re.findall(r"\((.*?)\)", line.strip())
                indexed_names = re.split(r",\s*", matches[0])

                table.pk = indexed_names
            else:
              field = Field()

              # get field name and type
              comment_idx: None | int = None
              for i, token in enumerate(tokens):
                  if token == "--":
                      comment_idx = i
                      break
                  elif i == 0:
                      field.name = token
                  elif i == 1:
                      field.type = token.replace(",", "")

              # join comments
              comment_tokens: list[str] = []
              if comment_idx != None:
                  comment_tokens = tokens[(comment_idx + 1):]

              field.comment = " ".join(comment_tokens)

              # add to table
              table.fields.append(field)
  
    return table

def main():
    if len(sys.argv) != 3:
        raise Exception("The command requires two arguments to execute <src-dir> and <out-dir>.")

    [ prog, src_dir, out_dir ] = sys.argv

    abs_src_dir = os.path.abspath(src_dir)
    abs_out_dir = os.path.abspath(out_dir)

    tables = extract_src(abs_src_dir)

    for table in tables:
        print(table.to_d2_format())

if __name__ == "__main__":
    main()
