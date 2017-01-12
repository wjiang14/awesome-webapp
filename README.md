# awesome-python3-webapp

it is based [廖雪峰's](http://http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000) python3 project

## Develoment Environment

```bash
python3 --version
Python 3.5.2
```

we need aiohttp (asynchronous) and jinja2 (templating language for Python) modules
we just need to type pip3 install

```bash
pip3 install aiohttp
```

```bash
pip3 install jinja2
```

Because our webapp need a database, we choose mySQL. for Mac User, we recommend use homebrew install
```bash
brew install mySQL
```
windows user please go to [Oracle website](http://dev.mysql.com/downloads/mysql/5.6.html) to download
python drive module of mySQL is aiomysql
```bash
pip3 install aiomysql
```

## Project Structure

* awesome-python3-webapp/ 
|
* +- backup/&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; &emsp;<-- backup
|
* +- www/ &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; &emsp;&emsp;<-- web
* | &ensp;  +- static/+- static/&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;<-- static file (css)
* | &ensp;  |
* | &ensp;  +- templates/templates/&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;<-- HTML template
* |
* +- LICENSE               <-- LICENSE
