# What is this?

Currently just a python module to easily make an IRC client.
It also has bot support (the main reason for doing this).

## How to make a bot

Bots need an address, port, channel to connect, as well as a name, and optionally a bang and some functions.

Before the fun begins you need to connect to the server, register and join a channel, then run the bot.

All functions need to take in two arguments, the Bot instance and the IRC\_Message sent.

```
import irc

def hello(b, m):
    return f'Hello {m.nickname}!'

if __name__ == '__main__':
    functions = [('hello', hello)]
    bot = irc.Bot('irc.example.org',6667,'#bot','bot',
                   bang='!',functions=functions)
    bot.connect()
    bot.register()
    bot.join('#bot')
    while True:
        bot.run()
```

The example bot will join the channel #bot on inc.example.org and when someone writes '!hello' it will respond with 'Hello *nickname*' where *nickname* is the nickname of the person who sent the message.
