import drive_service, httplib2, csv, json, configparser
from apiclient import discovery

def get_drive_service():
    credentials = drive_service.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service

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

def read_csv(csv_file, json_file, headers):
    csvfile = open(csv_file, 'r')
    jsonfile = open(json_file, 'w')

    reader = csv.DictReader(csvfile, headers)
    for i, row in enumerate(reader):
        if i > 1:
            json.dump(row, jsonfile)
            jsonfile.write('\n')

def main():
    # TODO: Include command line flag to pull files from drive
    # The option could take input in yyyy-mm-dd format to find the right files or do it automatically somehow
    # service = get_drive_service()
    # csv_folder = get_csv_folder(service)

    # if csv_folder:
    #     expense_files = service.files().list(
    #         q='"' + csv_folder['id'] + '" in parents').execute()
    #     items = expense_files.get('files', [])
    #     for item in items:
    #         print('{0} {1}'.format(item['name'], item['id']))
    # else:
    #     print('No expense data found')

    # Open our expenses config file
    configParser = configparser.RawConfigParser()
    configPath = './expenses-config.txt'
    configParser.read(configPath)

    # Load account and header info from config file
    accounts = configParser.get('Accounts', 'account_names').split(', ')
    headers = json.loads(configParser.get('Accounts', 'headers'))

    for account in accounts:
        read_csv('expense_sheets/2017-05-20_' + account + '.csv', 'json_data/' + account + '.json', headers)

if __name__ == '__main__':
    main()