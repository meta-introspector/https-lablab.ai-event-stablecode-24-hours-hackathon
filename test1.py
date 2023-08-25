import click
import io
import sys

from transformers import AutoModelForCausalLM, AutoTokenizer

import warnings
# Suppress the specific warning message
warnings.filterwarnings("ignore", category=UserWarning, message="Setting `pad_token_id` to `eos_token_id`:0 for open-end generation")


def instruction(inputa):
    return f"""###Instruction
    {inputa} 
    ###Response
"""

from transformers import pipeline
chatbot_state = {
    "current_line": 0,
    "width": 3,
    "temp": 0.5,
    "max_length":5000,
    "gas_remaining": 100,
    "tape" : []
}

tokenizer= None
model = None

def printline():
    width = int(chatbot_state['width'])
    if int(chatbot_state['current_line']) <  len(chatbot_state['tape'])-width:
        clin  = int(chatbot_state['current_line'])
        line = chatbot_state['tape'][clin:clin+width] 
        
        click.echo(f"Line:{clin}:{line}.")
    else:
        click.echo(f"Chatbot: debug {chatbot_state['current_line']}")
        click.echo(f"Chatbot: tape {len(chatbot_state['tape'])}")
        

def load():
    global tokenizer
    global model
    global chatbot_state
    print("loading")
    tokenizer = AutoTokenizer.from_pretrained("stabilityai/stablecode-instruct-alpha-3b")
    model = AutoModelForCausalLM.from_pretrained(
        "stabilityai/stablecode-instruct-alpha-3b",
  trust_remote_code=True,
        torch_dtype="auto",
    )
    model.cuda()
    click.echo("loaded")
                                               
@click.command()
@click.argument('file1', type=click.File('r'))
def execute(file1):
    # Read lines from both files
    lines_file1 = file1.readlines()    
    chatbot_state["tape"]  =lines_file1
    #load()
    main_loop()

@click.group()
def chatbot():
    pass

@chatbot.command()
def start():
    click.echo("Welcome to the Chatbot! Type --help to see available commands.")
    printline()
    click.echo(click.Context(chatbot).get_help())

@chatbot.command()
def help():
    click.echo("Welcome to the Chatbot Monad where you the chat control the situation! Type help to see available commands.")
    printline()
    click.echo(click.Context(chatbot).get_help())


@chatbot.command()
def next():
    click.echo("Reading Next Line")
    global chatbot_state

    if int(chatbot_state['current_line']) <  len(chatbot_state['tape']):
        chatbot_state['current_line']=  int(      chatbot_state['current_line']) + 1        
    else:
        click.echo("EOF")
    printline()
    click.echo(f"gas remaining {chatbot_state['gas_remaining']}")

@chatbot.command()
@click.argument('args', nargs=-1)
def echo(args):
    """Echo all provided arguments."""
    message = ' '.join(args)
    click.echo(message)

@chatbot.command()
def repeat():
    click.echo("Repeat")
    printline()
        
@chatbot.command()
def prev():
    click.echo("prev")
    global chatbot_state
    if int(chatbot_state['current_line']) > 0:
        chatbot_state['current_line']=  int(      chatbot_state['current_line']) -1 
    else:
        click.echo("BOF")
    printline()
    click.echo(f"gas remaining {chatbot_state['gas_remaining']}")
        

@chatbot.command()
def exit():
    click.echo("Goodbye! Chatbot is exiting.")


def process_user_command(user_input):
    try:
        args = user_input.split()
        ctx = click.Context(chatbot, info_name=args[0])
        chatbot.main(args, parent=ctx)
    except SystemExit:
        pass

def consume_gas(gas_cost=1):
    global chatbot_state
    if chatbot_state["gas_remaining"] >= gas_cost:
        chatbot_state["gas_remaining"] -= gas_cost

        return True
    else:
        click.echo("Chatbot: Error: Not enough gas remaining to perform this action.")
        return False
# Create an in-memory text stream

    
def main_loop():


    #help = click.Context(chatbot).get_help()
    user_input = "Help"
        
    while True:        
        original_stdout = sys.stdout
        output_stream = io.StringIO()
        sys.stdout = output_stream
        
        with output_stream as stream:

            if not consume_gas(gas_cost=1):
                return
        
            if user_input.lower() == "exit":
                click.echo("Chatbot: Goodbye!")
                break

            process_user_command(user_input)
            captured_output = stream.getvalue()
            
        sys.stdout = original_stdout        
    
        #print("Captured Output:")
        #print(captured_output)
        
        res= send_to_model(user_input + " Produced " + captured_output)
        #print(f"Response: {res}" )
        user_input = click.prompt("You: ", type=str)
        #res2= send_to_model(user_input)
        #print(f"Response2: {res2}" )



#text = generator("Albert Einstein was:", max_length=10, pad_token_id=50256, num_return_sequences=1)
#text = generator("Albert Einstein was:", max_length=10, num_return_sequences=1)

def send_to_model(user_input):

    print(f"DEBUG IN {user_input}")
    inputa = instruction(user_input)
    inputs = tokenizer(inputa, return_tensors="pt").to("cuda")
    tokens = model.generate(
        **inputs,
        max_length=5000,
        temperature=0.2,
        pad_token_id=50256,
        do_sample=True,
        num_return_sequences=1
        )
    response = tokenizer.decode(tokens[0], skip_special_tokens=True)
        
    click.echo(f"Chatbot OUT:{response}")
    #print(f"DEBUG OUT{response}")
    return response


if __name__ == '__main__':
    load()
    execute()





    
