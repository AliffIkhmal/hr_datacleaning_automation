import unittest

import pandas as pd

from hr_cleaning.cleaner import clean_hr_data


class CleanerRulesTests(unittest.TestCase):
    def test_rejects_non_hr_dataset(self):
        df = pd.DataFrame({"x": [1], "y": [2], "z": [3]})
        with self.assertRaises(ValueError):
            clean_hr_data(df)

    def test_strict_mode_requires_all_core_columns(self):
        df = pd.DataFrame(
            {
                "Name": ["Siti Aminah"],
                "Gender": [None],
                "Salary": [12000],
                "Age": [25],
            }
        )
        with self.assertRaises(ValueError):
            clean_hr_data(df, strict_mode=True)

    def test_gender_inference_and_salary_handling(self):
        df = pd.DataFrame(
            {
                "Name": ["Siti Aminah", "Muhammad Firdaus", "Unknown Person"],
                "Gender": [None, None, None],
                "Salary": [15000, 120000, 200000],
                "Age": [7, 35, 40],
                "Performance Rating": [4, 6, 5],
                "Overtime Hours": [1, 2, 3],
            }
        )

        cleaned_df, stats, outliers_df = clean_hr_data(df)

        self.assertEqual(cleaned_df.loc[0, "Gender"], "Female")
        self.assertEqual(cleaned_df.loc[1, "Gender"], "Male")
        self.assertTrue(pd.isna(cleaned_df.loc[2, "Gender"]))

        self.assertEqual(stats["outliers_detected"], 2)
        self.assertEqual(len(outliers_df), 2)
        self.assertTrue((cleaned_df["Salary"] < 100000).all())
        self.assertTrue((cleaned_df["Age"] >= 10).all())
        self.assertEqual(int(cleaned_df["Performance Rating"].max()), 5)


if __name__ == "__main__":
    unittest.main()
