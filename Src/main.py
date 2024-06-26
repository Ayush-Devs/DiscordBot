import os
import discord
import random
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv("GEMINI"))

# Set up intents
intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        help_text = "Here's how to use the bot:\n"
        for command in bot.commands:
            help_text += f"!{command} - {command.help}\n"
        await self.get_destination().send(help_text)

# Set the custom help command
bot.help_command = CustomHelpCommand()

# gemini api
def get_gemini_response(question):
    response = genai.GenerativeModel('gemini-pro').generate_content(question)
    return response.text

# Game state for tic-tac-toe
ttt_board = [" " for _ in range(9)]
player_turn = "X"

def print_board():
    row1 = "|".join(ttt_board[0:3])
    row2 = "|".join(ttt_board[3:6])
    row3 = "|".join(ttt_board[6:9])
    return f"```\n{row1}\n-----\n{row2}\n-----\n{row3}\n```"

def check_winner(board, player):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
        [0, 4, 8], [2, 4, 6]             # Diagonal
    ]
    return any(all(board[i] == player for i in condition) for condition in win_conditions)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
    else:
        user_message = message.content
        gemini_response = get_gemini_response(user_message)
        await message.channel.send(gemini_response)

@bot.command(name='ttt', help='Play tic-tac-toe. Use !ttt [position 1-9]')
async def tic_tac_toe(ctx, position: int):
    global player_turn
    if not 1 <= position <= 9:
        await ctx.send("Please enter a valid position (1-9).")
        return

    position -= 1  # Adjust for zero-indexed list
    if ttt_board[position] == " ":
        ttt_board[position] = player_turn
        if check_winner(ttt_board, player_turn):
            await ctx.send(f"{player_turn} wins!")
            ttt_board[:] = [" " for _ in range(9)]  # Reset the board
        elif " " not in ttt_board:
            await ctx.send("It's a tie!")
            ttt_board[:] = [" " for _ in range(9)]
        else:
            player_turn = "O" if player_turn == "X" else "X"
            await ctx.send(print_board())
    else:
        await ctx.send("That spot is taken!")

@bot.command(name='guess', help='Guess a number between 1 and 10. Use !guess [number]')
async def guess(ctx, number: int):
    secret_number = random.randint(1, 10)
    if number == secret_number:
        await ctx.send("You guessed it right!")
    else:
        await ctx.send(f"Wrong! The correct number was {secret_number}.")

# Run the bot
bot.run(TOKEN)
