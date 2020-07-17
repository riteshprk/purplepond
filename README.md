# E-Commerce website 

This is a fully functional e-commerce website built with Django, Python.

## Quick demo

<p align="center">
  <a href="https://puplepond.herokuapp.com">
    <img src="./media/purplepondhome.png" alt="PurplePond Logo">
  </a>
</p>
---
 <p align="center">
    <a href="https://purplepond.herokuapp.com">View Demo</a>
    ·
    <a href="https://github.com/riteshprk/purplepond/issues">Report Bug</a>
    ·
    <a href="https://github.com/riteshprk/purplepond/issues">Request Feature</a>
  </p>

## ✨ Features

- Categories display and search
- Quantity and Size selection
- Modify cart
- Discont coupon 
- Payment method- Stripe and Paypal
- Order confirmation and Order history
- User account handling

## Tech Stack

| Stack    | -                                                                                                  | -                                                                                                 | -                                                                                                 | 
| -------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | 
| FrontEnd | <p align="center"><img src="./media/html.png" width="100" height="100"> <br />HTML</p> | <p align="center"><img src="./media/css.png" width="100" height="100"> <br />CSS</p>  |  <p align="center"><img src="./media/js.png" width="100" height="100"> <br />JavaScript</p>  | 
| BackEnd  | <p align="center"><img src="./media/python.png" width="100" height="100"> <br />Python</p>   | <p align="center"><img src="./media/django.png" width="100" height="100"> <br />Django</p> |


## :rocket: Quick start

Start developing locally.

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
virtualenv env
```

That will create a new folder `env` in your project directory. Next activate it with this command on mac/linux:

```
source env/bin/active
```

Then install the project dependencies with

```
pip install -r requirements.txt
```

Now you can run the project with this command

```
python manage.py runserver
```

**Note** if you want payments to work you will need to enter your own Stripe API keys into the `.env` file in the settings files.



---

## Support

If you'd like to support this project and all the other open source work on this organization, you can use the following options

### GitHub Sponsors

Sponsor through GitHub Sponsors. On GitHub, [this repository](https://github.com/riteshprk/purplepond) shows a button where you can Sponsor the contributors.


Made with ❤️ and Python