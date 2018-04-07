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
Some log will print on your terminal and the server will start running on the address `http://0.0.0.0:5000/`. Check in your browser the address `http://0.0.0.0:5000/all`, and it should print a big json. This is our API retriving data from codepit :)

Now you need to open `/local-path/desafios-ranking/front-end/index.html` on your broswer as well. Don't forget to replace `/local-path/` with the path where you cloned this repo.

If everything just went fine, you can see now the score board on your browser.

## Contributing

This isn't quite an ambitious project, but you are free to fork it, make cool changes and send a pull request with new features that you think would improve the project.

## Credits

- [Italo Nicola](https://github.com/nyeecola)
- [André Almeida](https://github.com/andrealmeid)

## License

MIT License
