# desafios-ranking

__desafios-ranking__ is the a competitive programming leaderboard, but it doesn't ranks the competitors, it ranks the _problems_ instead.
This ranking is exclusively to the problems of Unicamp's competitive programming classes, updated at least on a daily basis. The problems are hosted in [codepit.io](https://codepit.io/), a online judge (like [UVa](https://uva.onlinejudge.org/)).

## Installation

First, clone this repo:
```bash
$ git clone https://github.com/nyeecola/desafios-ranking.git
```
Then check if you the requirements are satisfied:
- Flask
- Tabulate
- Requests

If you don't, just install they using:
```bash
$ sudo pip install [requirement name here]
```

We are almost done! Create a file named `credentials.txt` and paste there your credentials to codepit.io, like this:
```
myemail@email.com;my_password
```
This file must be placed on the same directoty as `main.py`.

## Usage

Now, we can test the server on our local machine. Let's start it!
```bash
$ python3 main.py
```
Some log will print on your terminal and the server will start running.

## Contributing

## Credits

## License
