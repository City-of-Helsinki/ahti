# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_create_feature 1"] = {
    "data": {
        "createFeature": {
            "feature": {
                "geometry": {"coordinates": [24.940967, 60.168683], "type": "Point"},
                "properties": {
                    "category": None,
                    "contactInfo": {
                        "address": {
                            "municipality": "Helsinki",
                            "postalCode": "00100",
                            "streetAddress": "Street 123",
                        },
                        "email": "email@example.com",
                        "phoneNumber": "+358501234567",
                    },
                    "source": {"system": "ahti", "type": "api"},
                    "tags": [],
                    "translations": [
                        {
                            "description": "Feature description",
                            "languageCode": "FI",
                            "name": "Feature name",
                            "oneLiner": "Feature tagline",
                            "url": "www.url.com",
                        }
                    ],
                },
            }
        }
    }
}
