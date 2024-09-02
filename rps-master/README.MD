## Rock Paper Scissors Script with an LS extra

### Classic *!rps*

    Scissors cuts Paper 
    Paper covers Rock 
    Rock crushes Scissors 

Boring? Look further down

### Lizard Spock *!rpsls*
    Scissors cuts Paper 
    Paper covers Rock 
    Rock crushes Lizard 
    Lizard poisons Spock 
    Spock smashes Scissors 
    Scissors decapitates Lizard 
    Lizard eats Paper 
    Paper disproves Spock 
    Spock vaporizes Rock 
    (and as it always has) Rock crushes Scissor

- http://www.samkass.com/theories/RPSSL.html
- https://bigbangtheory.fandom.com/wiki/Rock,_Paper,_Scissors,_Lizard,_Spock

### Settings
* **Classic - command** (classic_command) - Command to play the classic "Rock, Paper, Scissors". Empty to disable
* **Lizard, Spock - command** (lizardspock_command) - Command to play "Rock, Paper, Scissors, Lizard, Spock". Empty to disable
* **Localisation** (localisation_file) - Name of the file containing desired localisation.
* **Winner gets currency** (reward) - Amount of Chatbot currency to give when someone wins against the bot.
* **User cooldown** (user_cooldown) - In seconds - Cooldown per user preventing abuse.

### Localisation
**#** is a reserved characters for comments `# Comments in file`

2 language are supported for the moment but you can easily tweake the code to add yours.
1. Copy *local_en.txt* and rename it
2. Translate and customize your message
3. Add the new file name in this list (*UI_Config.json* line 21)

##### Messages parameters: 
- `{user}` : Username 
- `{phrase}` : Simple phrase like "Paper covers Rock". *N/A on equality*. 
- `{user_pick}` : Show user choice like "Paper" 
- `{bot_pick}` : Show bot choice like "Rock"

### Usages vs bot
`!rps` + Rock, Paper or Scissors

`!rpsls` + Rock, Paper, Scissors, Lizard, Spock
