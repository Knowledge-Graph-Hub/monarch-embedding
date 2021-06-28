#!/usr/bin/env python3

import os
import sys
import subprocess
import silence_tensorflow.auto
from downloaders import BaseDownloader
from ensmallen_graph import EnsmallenGraph
from embiggen.utils import compute_node_embedding
import logging
import boto3
from botocore.exceptions import ClientError

nodes_url = "https://archive.monarchinitiative.org/202012/kgx/sri-reference-kg_nodes.tsv.gz"
edges_url = "https://archive.monarchinitiative.org/202012/kgx/sri-reference-kg_edges.tsv.gz"
s3_bucket = "kg-hub-public-data"
s3_bucket_dir = "monarch" # where in s3://kg-hub-public-data where we want to put this

embedding_method = "SkipGram"
graph_name = "FilteredMonarch"

local_emb_dir = "/".join(["node_embeddings", embedding_method, graph_name])


def upload_dir_to_s3(local_directory: str, s3_bucket: str, s3_bucket_dir: str, make_public=False) -> None:
    client = boto3.client('s3')
    for root, dirs, files in os.walk(local_directory):

        for filename in files:
            local_path = os.path.join(root, filename)

            # construct the full path
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(s3_bucket_dir, relative_path)

            print(f"Searching {s3_path} in {s3_bucket}")
            try:
                client.head_object(Bucket=s3_bucket, Key=s3_path)
                logging.warning("Existing file {s3_path} found on S3! Skipping.")
            except ClientError:  # Exception abuse
                ExtraArgs = None
                if make_public:
                    ExtraArgs = {'ACL': 'public-read'}

                logging.info(f"Uploading {s3_path}")
                client.upload_file(local_path, s3_bucket, s3_path, ExtraArgs=ExtraArgs)



print("running as:", subprocess.getoutput("whoami"))

print("downloading graph...", file=sys.stderr)

downloader = BaseDownloader()
downloader.download([
    nodes_url,
    edges_url
])

print("loading graph into EnsmallenGraph...", file=sys.stderr)
monarch = EnsmallenGraph.from_unsorted_csv(
    edge_path="downloads/sri-reference-kg_edges.tsv",
    directed=False,
    #node_path="downloads/sri-reference-kg_nodes.tsv",
    sources_column= "subject",
    destinations_column= "object",
    #edge_types_column= "relation",
    #nodes_column= "id",
    #node_types_column= "category",
    #node_types_separator= "|",
    #default_node_type= "biolink:NamedThing",
    edge_list_is_correct=True,
    #node_list_is_correct=True,
    #edge_max_rows_number=20000,
    name=graph_name)

print("dropping all but top 10 connected components...", file=sys.stderr)
filtered_monarch = monarch.remove_components(
    top_k_components=10,
    verbose=True
)

print(filtered_monarch.hash())

print("running embedding...", file=sys.stderr)
embedding, history = compute_node_embedding(
    graph=monarch,
    node_embedding_method_name=embedding_method,
    verbose=2,
    iterations=1,
    embedding_size=20,
    walk_length=128,
    window_size=3,
    batch_size=2048
)

print("uploading files...", file=sys.stderr)
upload_dir_to_s3(local_directory=local_emb_dir,
                 s3_bucket=s3_bucket,
                 s3_bucket_dir="/".join([s3_bucket_dir, local_emb_dir]),
                 make_public=True)
