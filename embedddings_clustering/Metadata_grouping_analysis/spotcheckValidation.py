import pandas as pd
import itables
from itables import show
from IPython.display import display
import numpy as np

class spotcheckValidation:

    def summarise_report(selected_df, meta_grouping_df, label_key, parent_key, parent_values):
        # print(f"""{label_key}\n{selected_df.head()}\n{meta_grouping_df.columns}\n""")

        key_value = dict(zip(parent_key, parent_values))
        parsed_group_prompt_filter = 'PID-' + '-'.join(parent_values)
        parent_filtered_df = meta_grouping_df[meta_grouping_df['prompt_name'].str.startswith(parsed_group_prompt_filter)]

        label_count = pd.DataFrame(parent_filtered_df[f'{label_key}'].value_counts())
        label_names = label_count.index.tolist()
        summary_df = pd.DataFrame()
        summary_df[f'{label_key}'] = label_names

        # Expected counts
        expected_question_count = selected_df[selected_df[f'{label_key}_meta'].isin(label_names)] \
            .groupby(f'{label_key}_meta')['question_id'].count()
        summary_df['expected question cnt (metadata)'] = summary_df[f'{label_key}'].map(expected_question_count)

        # Actual counts
        actual_question_count = selected_df[selected_df[f'{label_key}_cluster'].isin(label_names)] \
            .groupby(f'assigned_{label_key}')['question_id'].count()
        summary_df['actual question cnt (cluster)'] = summary_df[f'{label_key}'].map(actual_question_count)

        # Get the first cluster from the unique array directly during groupby
        actual_cluster = (
            selected_df[selected_df[f'{label_key}_cluster'].isin(label_names)]
            .groupby(f'assigned_{label_key}')['cluster']
            .agg(lambda x: x.unique()[0])  # pick the first unique cluster
        )
        # Map it directly to summary_df
        summary_df['actual_cluster'] = summary_df[f'{label_key}'].map(actual_cluster)

        # Confusion matrix
        confusion_df = selected_df[
            (selected_df[f'{label_key}_meta'].isin(label_names)) &
            (selected_df[f'assigned_{label_key}'].isin(label_names))
        ].groupby([f'assigned_{label_key}', f'{label_key}_meta'])['question_id'].count().unstack(fill_value=0)

        # Add confusion matrix counts
        for meta_label in confusion_df.columns:
            summary_df[f'{meta_label}_cnt'] = summary_df[f'{label_key}'].map(confusion_df[meta_label])

        # Add normalized percentage columns
        for meta_label in confusion_df.columns:
            norm_col = f'{meta_label} %'
            summary_df[norm_col] = summary_df[f'{label_key}'].map(
                (confusion_df[meta_label] / confusion_df.sum(axis=1) * 100).round(2)
            )

        # Accuracy per label: correct / total actual
        def calc_accuracy(row):
            label = row[label_key]
            correct = row.get(f'{label}_cnt', 0)
            total = row.get('actual question cnt (cluster)', 0)
            return round((correct / total) * 100, 2) if total > 0 else 0

        summary_df['accuracy %'] = summary_df.apply(calc_accuracy, axis=1)
        # print(summary_df.to_string(index=False))


        return summary_df

        # # Overall accuracy
        # total_correct = sum(confusion_df[label].get(label, 0) for label in confusion_df.columns)
        # total_predictions = confusion_df.values.sum()
        # overall_accuracy = round(total_correct / total_predictions * 100, 2) if total_predictions > 0 else 0

        # # Format the table for better display
        # pd.set_option('display.max_columns', None)  # Show all columns
        # pd.set_option('display.width', None)  # Don't wrap wide tables
        # pd.set_option('display.max_rows', None)  # Show all rows
        
        # # Display the formatted table
        # print("\nValidation Summary:")
        # print("=" * 100)
        # print("=" * 100)
        # print(f"\n Overall Accuracy: {overall_accuracy}%")




    # def summarise_report(selected_df, meta_grouping_df, label_key, parent_key, parent_values):
    #     print(f"""{label_key}\n{selected_df.head()}\n
    #     {meta_grouping_df.columns}\n""")

    #     key_value = dict(zip(parent_key, parent_values))
    #     parsed_group_prompt_filter = 'PID-' + '-'.join(parent_values)
    #     parent_filtered_df = meta_grouping_df[meta_grouping_df['prompt_name'].str.startswith(parsed_group_prompt_filter)]

    #     label_count = pd.DataFrame(parent_filtered_df[f'{label_key}'].value_counts())
    #     label_names = label_count.index.tolist()
    #     summary_df = pd.DataFrame()
    #     summary_df[f'{label_key}'] = label_names

    #     # Expected counts
    #     expected_question_count = selected_df[selected_df[f'{label_key}_meta'].isin(label_names)] \
    #         .groupby(f'{label_key}_meta')['question_id'].count()
    #     summary_df['expected_question_count(metadata)'] = summary_df[f'{label_key}'].map(expected_question_count)

    #     # Actual counts
    #     actual_question_count = selected_df[selected_df[f'{label_key}_cluster'].isin(label_names)] \
    #         .groupby(f'assigned_{label_key}')['question_id'].count()
    #     summary_df['actual_question_count(cluster)'] = summary_df[f'{label_key}'].map(actual_question_count)

    #     # Dynamic confusion matrix counts
    #     confusion_df = selected_df[
    #         (selected_df[f'{label_key}_meta'].isin(label_names)) &
    #         (selected_df[f'assigned_{label_key}'].isin(label_names))
    #     ].groupby([f'assigned_{label_key}', f'{label_key}_meta'])['question_id'].count().unstack(fill_value=0)

    #     # Add confusion matrix columns to summary_df
    #     for meta_label in confusion_df.columns:
    #         summary_df[f'{meta_label}_count'] = summary_df[f'{label_key}'].map(confusion_df[meta_label])

    #     print(summary_df.head(10))
        # return summary_df

    # @staticmethod
    def validateAndReturnDF(metadata_path: str, labelled_KMeans_path: str, label_key: str, parent_key: list, parent_values: tuple):

        meta_grouping_df = pd.read_csv(metadata_path)
        k_4_cluster_df = pd.read_csv(labelled_KMeans_path)

        meta_grouping_df = meta_grouping_df.drop(columns=['vector', 'x', 'y'], errors='ignore')
        k_4_cluster_df = k_4_cluster_df.drop(columns=['vector', 'x', 'y'], errors='ignore')

        print("==========", k_4_cluster_df.columns,'\n', k_4_cluster_df.head(10),'\nna: ',k_4_cluster_df.isna().sum(), '\nnull:', k_4_cluster_df.isnull().sum())

        meta_grouping_df = meta_grouping_df.sort_values(by=['subject', 'domain', 'skill', 'subskill', 'difficulty'])

        merged_df = meta_grouping_df.merge(k_4_cluster_df, on='question_id', suffixes=('_meta', '_cluster'))
        print("==========", merged_df.columns,'\n', merged_df.head(10),'\nna: ',merged_df.isna().sum(), '\nnull:', merged_df.isnull().sum())
        print("****\nMerged DataFrame:\n", merged_df.where(merged_df['cluster'].isnull()))


        cluster_label_map = (
            merged_df.groupby('cluster')[f'{label_key}_meta']
            .agg(lambda x: x.value_counts().index[0])
            .to_dict()
        )

        merged_df[f'assigned_{label_key}'] = merged_df['cluster'].map(cluster_label_map)
        merged_df['is_correct'] = merged_df[f'{label_key}_meta'] == merged_df[f'assigned_' + label_key]

        selected_columns = ['question_id', f'{label_key}_meta', f'{label_key}_cluster', 'cluster', f'assigned_{label_key}', 'is_correct']
        selected_df = merged_df[selected_columns]

        # def color_row(val):
        #     return 'background-color: lightgreen' if val else 'background-color: lightcoral'

        # styled_selected_df = selected_df.style.applymap(color_row, subset=['is_correct'])
        # styled_selected_df.to_html("selected_columns_colored.html", escape=False)

        itables.options.lengthMenu = [[10, 25, 50, -1], [10, 25, 50, "All"]]
        itables.options.maxBytes = 0
        itables.options.columnDefs = [{"targets": "_all", "className": "dt-center"}]

        # Repeat selection again as per original logic
        selected_columns = ['question_id', f'{label_key}_meta', f'{label_key}_cluster', 'cluster', f'assigned_{label_key}', 'is_correct']
        selected_df = merged_df[selected_columns]

        df_summary = spotcheckValidation.summarise_report(selected_df, meta_grouping_df, label_key, parent_key, parent_values)

        def color_row(val):
            return 'background-color: lightgreen' if val else 'background-color: lightcoral'

        styled_selected_df = selected_df.style.applymap(color_row, subset=['is_correct'])

        return styled_selected_df, df_summary


if __name__ == "__main__":
    c,d = spotcheckValidation.validateAndReturnDF(
        metadata_path=r'C:\Users\Manideep S\Downloads\subject-M.csv', 
        labelled_KMeans_path=r'C:\Users\Manideep S\Downloads\subject-M_domain_labelcount_kmeans.csv',
        label_key='domain',
        # key_value = {'subject': 'M','domain': 'ALG'},
        parent_key=['subject'],
        parent_values=('M')
        )

    # print(d) 
    print("--------------\n",d.where(d['actual_cluster'].isnull()).head(10)) 

# subject = 'M' -> 'd1','d2','d3','d4'
# domain = 'M','d1' -> 's1','s2','s3','s4'

