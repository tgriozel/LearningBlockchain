## Notes

This nothing more than a little piece of code I produced when learning about the blockchain technology. The proof of work algorithm is silly, and it has nothing to do with real world blockchains.

We serve some REST GET endpoints to interact with the blockchain: `get_chain`, `mine_block` and `is_valid`.
The server is running on port 5000.

Requirements: `python3` and `pipenv`

Run the simple blockchain: `pipenv run python3 blockchain.py`

Run the MyCoin blockchain: `pipenv run python3 mycoin.py $PORT`
