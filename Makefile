start-ipfs:
	docker run -p 5001:5001 -p 8080:8080 -p 4001:4001 -v ~/ipfs/ipfs_staging:/export -v ~/ipfs/ipfs_data:/data/ipfs ipfs/go-ipfs:v0.8.0

start-server:
	sudo uvicorn app:app --host 0.0.0.0 --port 8000 --reload