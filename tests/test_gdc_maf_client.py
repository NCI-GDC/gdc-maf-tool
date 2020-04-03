from httmock import HTTMock
from tests import mocks

from gdc_maf_tool.gdc_api_client import (
    _build_hit_map,
    _parse_hit,
    _select_mafs,
)


def test__select_mafs():
    results = {
        "warnings": {},
        "data": {
            "hits": [
                {
                    "cases": [
                        {
                            "project": {"project_id": "TARGET-AML"},
                            "case_id": "06cd1d5f-9918-5db2-8c0d-3a0cedea5748",
                            "samples": [
                                {
                                    "tissue_type": "Not Reported",
                                    "portions": [
                                        {
                                            "analytes": [
                                                {
                                                    "aliquots": [
                                                        {
                                                            "submitter_id": "TARGET-20-PANLRE-09A-01D"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                    "sample_type": "Primary Blood Derived Cancer - Bone Marrow",
                                },
                                {
                                    "tissue_type": "Not Reported",
                                    "portions": [
                                        {
                                            "analytes": [
                                                {
                                                    "aliquots": [
                                                        {
                                                            "submitter_id": "TARGET-20-PANLRE-14A-01D"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                    "sample_type": "Bone Marrow Normal",
                                },
                            ],
                        }
                    ],
                    "file_id": "080765f4-349d-4646-954c-9673fa2033e6",
                    "id": "080765f4-349d-4646-954c-9673fa2033e6",
                    "created_datetime": "2020-03-17T21:24:16.127588-05:00",
                    "file_size": 4771,
                    "md5sum": "192320bb88982621512869f50add3a20",
                },
                {
                    "cases": [
                        {
                            "project": {"project_id": "TARGET-AML"},
                            "case_id": "06cd1d5f-9918-5db2-8c0d-3a0cedea5748",
                            "samples": [
                                {
                                    "tissue_type": "Not Reported",
                                    "portions": [
                                        {
                                            "analytes": [
                                                {
                                                    "aliquots": [
                                                        {
                                                            "submitter_id": "TARGET-20-PANLRE-04A-01D"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                    "sample_type": "Recurrent Blood Derived Cancer - Bone Marrow",
                                },
                                {
                                    "tissue_type": "Not Reported",
                                    "portions": [
                                        {
                                            "analytes": [
                                                {
                                                    "aliquots": [
                                                        {
                                                            "submitter_id": "TARGET-20-PANLRE-14A-01D"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                    "sample_type": "Bone Marrow Normal",
                                },
                            ],
                        }
                    ],
                    "file_id": "3609f3b5-3827-4114-9529-e3e8e1998902",
                    "id": "3609f3b5-3827-4114-9529-e3e8e1998902",
                    "created_datetime": "2020-03-17T21:24:16.127588-05:00",
                    "file_size": 1050,
                    "md5sum": "50fafde798b8d533135a35d417ad164e",
                },
            ],
            "pagination": {
                "total": 2,
                "page": 1,
                "count": 2,
                "sort": "",
                "from": 0,
                "size": 5000,
                "pages": 1,
            },
        },
    }
    with HTTMock(mocks.download_mock):
        mafs = _select_mafs(
            _build_hit_map([_parse_hit(hit) for hit in results["data"]["hits"]]),
            mocks.VALID_TOKEN,
        )
    assert mafs[0].tumor_aliquot_submitter_id == "TARGET-20-PANLRE-09A-01D"
