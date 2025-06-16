import pandas as pd
import itables
from itables import show
from IPython.display import display
import numpy as np
from scipy.optimize import linear_sum_assignment

class spotcheckValidation_test:

    @staticmethod
    def summarise_report(selected_df, meta_grouping_df, label_key, parent_key, parent_values):
        parsed_group_prompt_filter = 'PID-' + '-'.join(parent_values)
        parent_filtered_df = meta_grouping_df[
            meta_grouping_df['prompt_name'].str.startswith(parsed_group_prompt_filter)
        ]

        label_names = parent_filtered_df[label_key].value_counts().index.tolist()
        summary_df = pd.DataFrame({label_key: label_names})

        # Expected counts
        exp_cnt = (
            selected_df[selected_df[f"{label_key}_meta"].isin(label_names)]
            .groupby(f"{label_key}_meta")["question_id"]
            .count()
        )
        summary_df["expected question cnt (metadata)"] = summary_df[label_key].map(exp_cnt)

        # Actual counts
        act_cnt = (
            selected_df[selected_df[f"{label_key}_cluster"].isin(label_names)]
            .groupby(f"assigned_{label_key}")["question_id"]
            .count()
        )
        summary_df["actual question cnt (cluster)"] = summary_df[label_key].map(act_cnt)

        # Build confusion matrix
        confusion_df = (
            selected_df[
                (selected_df[f"{label_key}_meta"].isin(label_names))
                & (selected_df[f"assigned_{label_key}"].isin(label_names))
            ]
            .groupby([f"assigned_{label_key}", f"{label_key}_meta"])["question_id"]
            .count()
            .unstack(fill_value=0)
        )

        # Per-label “actual_cluster” (just the cluster index)
        actual_cluster = (
            selected_df[selected_df[f"{label_key}_cluster"].isin(label_names)]
            .groupby(f"assigned_{label_key}")["cluster"]
            .agg(lambda x: x.unique()[0])
        )
        summary_df["actual_cluster"] = summary_df[label_key].map(actual_cluster)

        # Confusion counts + normalized %
        for meta_label in confusion_df.columns:
            summary_df[f"{meta_label}_cnt"] = summary_df[label_key].map(confusion_df[meta_label])
            summary_df[f"{meta_label} %"] = summary_df[label_key].map(
                (confusion_df[meta_label] / confusion_df.sum(axis=1) * 100).round(2)
            )

        # Accuracy per label
        def calc_accuracy(row):
            lbl = row[label_key]
            correct = row.get(f"{lbl}_cnt", 0)
            total = row.get("actual question cnt (cluster)", 0)
            return round(correct / total * 100, 2) if total > 0 else 0

        summary_df["accuracy %"] = summary_df.apply(calc_accuracy, axis=1)
        return summary_df

    @staticmethod
    def validateAndReturnDF(metadata_path: str,
                            labelled_KMeans_path: str,
                            label_key: str,
                            parent_key: list,
                            parent_values: tuple):

        # 1. Load and preprocess
        meta_df = pd.read_csv(metadata_path)
        cluster_df = pd.read_csv(labelled_KMeans_path)
        for df in (meta_df, cluster_df):
            for col in ('vector','x','y'):
                if col in df.columns: 
                    df.drop(columns=col, inplace=True, errors='ignore')

        meta_df.sort_values(by=['subject','domain','skill','subskill','difficulty'], inplace=True)
        merged = meta_df.merge(cluster_df, on='question_id', suffixes=('_meta','_cluster'))

        # 2. Build confusion matrix: rows=cluster, cols=true labels
        labels = merged[f"{label_key}_meta"].unique().tolist()
        clusters = sorted(merged['cluster'].unique().tolist())
        confusion = (
            merged.groupby(['cluster', f"{label_key}_meta"])['question_id']
                  .count()
                  .unstack(fill_value=0)
                  .reindex(index=clusters, columns=labels, fill_value=0)
        )

        # 3. Hungarian assignment to maximize correct matches
        cost = -confusion.values
        row_ind, col_ind = linear_sum_assignment(cost)

        # 4. Build optimal mapping: cluster -> true label
        cluster_to_label = {
            clusters[row_ind[i]]: labels[col_ind[i]]
            for i in range(len(row_ind))
        }

        # 5. Assign back
        merged[f"assigned_{label_key}"] = merged['cluster'].map(cluster_to_label)
        merged['is_correct'] = merged[f"{label_key}_meta"] == merged[f"assigned_{label_key}"]

        # 6. Prepare display & summary
        selected_cols = ['question_id',
                         f"{label_key}_meta",
                         f"{label_key}_cluster",
                         'cluster',
                         f"assigned_{label_key}",
                         'is_correct']
        selected_df = merged[selected_cols]

        itables.options.lengthMenu = [[10,25,50,-1],[10,25,50,"All"]]
        itables.options.maxBytes = 0
        itables.options.columnDefs = [{"targets":"_all","className":"dt-center"}]

        summary_df = spotcheckValidation_test.summarise_report(
            selected_df, meta_df, label_key, parent_key, parent_values
        )

        # color styling: use .map instead of deprecated .applymap
        def color_row(val):
            return 'background-color: lightgreen' if val else 'background-color: lightcoral'

        styled = selected_df.style.map(color_row, subset=['is_correct'])

        return styled, summary_df


if __name__ == "__main__":
    styled_df, summary = spotcheckValidation_test.validateAndReturnDF(
        metadata_path=r'C:\Users\Manideep S\Downloads\subject-M.csv',
        labelled_KMeans_path=r'C:\Users\Manideep S\Downloads\subject-M_domain_labelcount_kmeans.csv',
        label_key='domain',
        parent_key=['subject'],
        parent_values=('M',)
    )

    # display styled table in Jupyter
    show(styled_df)

    # print summary table
    print(summary)

