from this import d
import unittest
import json
from unittest import result
import app
import data_generators

class TestScoresInDict(unittest.TestCase):

    def test_scores_in_dict(self):
        """
        Test scores to dict fucntion
        """
        with open("test/data/metrics_1.json", "r") as datafile:
                data = json.load(datafile)

        with open("test/data/scores_1.json", "r") as datafile:
                result = json.load(datafile)
        
        scores = data_generators.scores_in_dict(data)
        
        self.assertEqual(scores, result)

    def test_distribution_of_scores(self):
        """
        Test distribution of scores function
        """
        with open("test/data/scores_1.json", "r") as datafile:
                data = json.load(datafile)

        # float keys cannot be encoded in JSON, so an external JSON is NOT used in this test
        result = { "F": {
                        "F3": {
                            0.0: 1,
                            0.7: 1,
                            0.85: 2,
                            1.0: 1
                        },
                        "F2": {
                            0.6: 1,
                            1.0: 4
                        },
                        "F1": {
                            0.8: 2,
                            1.0: 3
                        }
                    },
                    "A": {
                        "A3": {
                            0.0: 2,
                            0.5: 2,
                            1.0: 1
                        },
                        "A1": {
                            0.0: 2,
                            0.5: 1,
                            0.6: 1,
                            0.7: 1
                        }
                    },
                    "I": {
                        "I3": {
                            0.0: 5
                        },
                        "I2": {
                            0.0: 4,
                            0.5: 1
                        },
                        "I1": {
                            0.0: 5
                        }
                    },
                    "R": {
                        "R4": {
                            0.0: 4,
                            1.0: 1
                        },
                        "R3": {
                            0.0: 1,
                            1.0: 4
                        },
                        "R2": {
                            0.0: 4,
                            1.0: 1
                        },
                        "R1": {
                            0.0: 1,
                            1.0: 4
                        }
                    }
                }
        
        distribution = data_generators.distribution_of_scores(data)
        
        self.assertEqual(distribution, result)
    
    def test_generate_synthetic_score_sets(self):
        """
        Test generate synthetic score sets function
        """
        data = { "F": {
                        "F3": {
                            0.0: 1,
                            0.7: 1,
                            0.85: 2,
                            1.0: 1
                        },
                        "F2": {
                            0.6: 1,
                            1.0: 4
                        },
                        "F1": {
                            0.8: 2,
                            1.0: 3
                        }
                    },
                    "A": {
                        "A3": {
                            0.0: 2,
                            0.5: 2,
                            1.0: 1
                        },
                        "A1": {
                            0.0: 2,
                            0.5: 1,
                            0.6: 1,
                            0.7: 1
                        }
                    },
                    "I": {
                        "I3": {
                            0.0: 5
                        },
                        "I2": {
                            0.0: 4,
                            0.5: 1
                        },
                        "I1": {
                            0.0: 5
                        }
                    },
                    "R": {
                        "R4": {
                            0.0: 4,
                            1.0: 1
                        },
                        "R3": {
                            0.0: 1,
                            1.0: 4
                        },
                        "R2": {
                            0.0: 4,
                            1.0: 1
                        },
                        "R1": {
                            0.0: 1,
                            1.0: 4
                        }
                    }
                }

        with open("test/data/synt_scores_1.json", "r") as datafile:
                result = json.load(datafile)
        
        synthetic = data_generators.generate_synthetic_score_sets(data)
        
        self.assertEqual(synthetic, result)






