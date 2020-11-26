## Notes

This nothing more than a little piece of code I produced when learning about the blockchain technology. The proof of work algorithm is silly, and it has nothing to do with real world blockchains.

We serve some REST endpoints to interact with the blockchain: `get_chain`, `mine_block`, `is_valid`, `add_transaction`, `connect_node` and `replace_chain`.
The webserver is running on the port indicated as the argument 1 of the command line.

Requirements: `python3` and `pipenv`

Run the MyCoin blockchain: `pipenv run python3 mycoin.py $PORT`

