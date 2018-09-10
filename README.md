# Poker-on-the-internet
This project implements poker on the Internet. It will accept one to five players. More than five players tend to spread the deck out too much. Every player will need a public/private key to play. They will also need to have an account with the house. Startup will have to be coordinated amongst the players. Session keys will be established between the house and the players. The session key is used to encrypt players. cards and for players to sign their bets. The house is responsible for totaling the pot and announcing bets to all players and tracking players' banks. Session keys will be destroyed after players leaves a current session.

# Contributors:
* Timothy Fong
* Haely Shah
* Oliver Zhu

# Instructions:
pip install pycrypto py-bcrypt
