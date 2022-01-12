# Bypass ReCaptcha

- Bypass ReCaptcha is a Python script for dealing with recaptcha.

## Installation

- To use this script you need to have playwright installed.

```bash
pip install playwright requests
```
```bash
playwright install # This will install all the browsers, get more info at https://playwright.dev/python/
```
```bash
python3 main.py or python main.py
```
### This project uses wit to recognize the audio from RECAPTCHA
- Get the API key at: [WIT API](https://wit.ai/)

- Enter your API in recaptcha.py
## Usage

```python
# Wit.ai api access token
WIT_ACCESS_TOKEN = "YOUR_WIT_API_TOKEN"
```

## Contributing
- Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)