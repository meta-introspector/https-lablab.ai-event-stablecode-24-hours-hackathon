import click
import os.path
seen = {}
    
@click.command()
@click.argument('file1', type=click.File('r'))
@click.argument('file2', type=click.File('r'))
def execute(file1, file2):
    # Read lines from both files
    lines_file1 = file1.readlines()
    lines_file2 = file2.readlines()

    A = f"metaprogram A named '''{os.path.basename(file1.name)}''"
    B = f"data file B named '''{os.path.basename(file2.name)}''"
    header = f"We are going to apply the {A} to the {B}. But first we review {A}. "
    
    print(header)

    for j,cmd_line in enumerate(lines_file1):
        if len(cmd_line) < 5:
            continue
        result = f"prepare_plan({A},{j},'''" + cmd_line.strip() + " ''')"
        if result not in seen:
            print(result)
            seen[result] =1 
    print (f"Finished with preparing the metaprogram {B} for execution. Now to read the source line by line.");

    # Perform operations based on the lines from the files

    step = 0
    maxl = len(lines_file2) * len(lines_file1)
    for i,data_line in enumerate(lines_file2):
        if len(data_line) < 5:
            continue
        result = f"Now we we read line {B}:{j} '''" + data_line.strip() + " ''' and will prepare to apply the metaprogram."
        print(result)

        for j,cmd_line in enumerate(lines_file1):
            if len(cmd_line) < 5:
                continue
            result = f"Evaluate step {step} of {maxl} the metaprogram line {A}:{i} '''" + cmd_line.strip() + "'''" +f"applied to {B}:{j} '''" + data_line.strip() + " ''';"
            if result not in seen:
                print(result)
                seen[result] =1
            step = step + 1
        print (f"Finished with line line{B}:{j}");
        
    print (f"Finished with Apply");
    
if __name__ == '__main__':
    execute()

