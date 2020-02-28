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

snapshots["test_feature_contact_info 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "contactInfo": {
                                "address": {
                                    "municipality": "Helsinki",
                                    "postalCode": "00170",
                                    "streetAddress": "Katariinankatu 3",
                                },
                                "email": "ahti@localhost",
                                "phoneNumber": "+358401234567",
                            }
                        }
                    }
                }
            ]
        }
    }
}

snapshots["test_feature_opening_hours 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "openingHoursPeriods": [
                                {
                                    "comment": "Comment",
                                    "openingHours": [
                                        {
                                            "allDay": False,
                                            "closes": "23:00:00",
                                            "day": "MONDAY",
                                            "opens": "17:00:00",
                                        },
                                        {
                                            "allDay": True,
                                            "closes": None,
                                            "day": "TUESDAY",
                                            "opens": None,
                                        },
                                    ],
                                    "validFrom": "2020-05-01",
                                    "validTo": "2020-08-31",
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
}

snapshots["test_feature_category 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "category": {
                                "description": "Island description",
                                "id": "ahti:category:island",
                                "name": "Island",
                            }
                        }
                    }
                }
            ]
        }
    }
}

snapshots["test_feature_parents_and_children 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "properties": {
                            "ahtiId": "test:test:sid0",
                            "children": [{"properties": {"ahtiId": "test:test:sid1"}}],
                            "parents": [],
                        }
                    }
                },
                {
                    "node": {
                        "properties": {
                            "ahtiId": "test:test:sid1",
                            "children": [],
                            "parents": [{"properties": {"ahtiId": "test:test:sid0"}}],
                        }
                    }
                },
            ]
        }
    }
}

snapshots["test_feature_with_id 1"] = {
    "data": {"feature": {"properties": {"ahtiId": "test:test:sid0"}}}
}

snapshots["test_feature_with_ahti_id 1"] = {
    "data": {"feature": {"properties": {"ahtiId": "test:test:sid0"}}}
}

snapshots["test_feature_query_error 1"] = {
    "data": {"feature": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "You must provide either `id` or `ahtiId`.",
            "path": ["feature"],
        }
    ],
}
