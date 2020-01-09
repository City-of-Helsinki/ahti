# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_features_query 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "geometry": {
                            "coordinates": [24.940967, 60.168683],
                            "type": "Point",
                        },
                        "properties": {
                            "ahtiId": "test:test:sid0",
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "description": "Place X description",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place X",
                            "source": {"id": "sid0", "system": "test", "type": "test"},
                            "translations": [
                                {
                                    "description": "Place X description",
                                    "languageCode": "FI",
                                    "name": "Place X",
                                    "url": "https://ahti1.localhost",
                                }
                            ],
                            "url": "https://ahti1.localhost",
                        },
                        "type": "Feature",
                    }
                },
                {
                    "node": {
                        "geometry": {
                            "coordinates": [24.952222, 60.169494],
                            "type": "Point",
                        },
                        "properties": {
                            "ahtiId": "test:test:sid1",
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "description": "Place Y description",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place Y",
                            "source": {"id": "sid1", "system": "test", "type": "test"},
                            "translations": [
                                {
                                    "description": "Place Y description",
                                    "languageCode": "FI",
                                    "name": "Place Y",
                                    "url": "https://ahti2.localhost",
                                }
                            ],
                            "url": "https://ahti2.localhost",
                        },
                        "type": "Feature",
                    }
                },
            ]
        }
    }
}

snapshots["test_features_image_query 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "images": [
                                {
                                    "copyrightOwner": "Photo Grapher",
                                    "license": {"name": "License 0"},
                                    "url": "https://ahti1.localhost/image.png",
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
}

snapshots["test_features_tags_query 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "tags": [
                                {"id": "ahti:0", "name": "Tag 0"},
                                {"id": "ahti:1", "name": "Tag 1"},
                            ]
                        }
                    }
                }
            ]
        }
    }
}
