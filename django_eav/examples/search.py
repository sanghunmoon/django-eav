from elasticsearch_dsl import Search, Q

s = Search(index="eav")

query = Q(
    "bool",
    must=[Q("match", **{"attribute-1": "example text"})],  # AND 조건
    should=[  # OR 조건
        Q("term", **{"attribute-2": "keyword_value"}),
        Q("match", **{"attribute-1": "another example"}),
    ],
)
s = s.query(query)
s = s.sort("attribute-3")

response = s.execute()
