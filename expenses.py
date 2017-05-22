import drive_service, httplib2
from apiclient import discovery

def get_csv_folder(service):
    results = service.files().list(
        pageSize=1, q='mimeType="application/vnd.google-apps.folder" and name="expensemanager"', fields='nextPageToken, files(id, name)').execute()
    expense_folder = results.get('files', [])
    csv_folder = False
    if not expense_folder:
        return False
    else:
        expense_folder = expense_folder[0]

        csv_folder_results = service.files().list(
            pageSize=10, q='"' + expense_folder['id'] + '" in parents', fields='nextPageToken, files(id, name)').execute()
        items = csv_folder_results.get('files', []);
        if not results:
            return False
        else:
            for item in items:
                if item['name'] == 'csv':
                    csv_folder = item
                    break

            if not csv_folder:
                return False
            else:
                return csv_folder


def main():
    credentials = drive_service.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)


    csv_folder = get_csv_folder(service)

    if csv_folder:
        expense_files = service.files().list(
            q='"' + csv_folder['id'] + '" in parents').execute()
        items = expense_files.get('files', [])
        for item in items:
            print('{0} {1}'.format(item['name'], item['id']))
    else:
        print('No expense data found')


if __name__ == '__main__':
    main()