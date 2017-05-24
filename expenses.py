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
    csv_file_instance = open(csv_file, 'r')
    json_file_instance = open(json_file, 'w')
    json_data = []

    reader = csv.DictReader(csv_file_instance, headers)
    for i, row in enumerate(reader):
        if i > 1:
            json_data.append(row)
            json.dump(row, json_file_instance)
            json_file_instance.write('\n')
    return json_data

# Take array of json objects, sum entries matching any keyword
def sum_entries(json_data, keyword_list):
    total = 0
    for entry in json_data:
        if keyword_list and keyword_list.length:
            if entry['Category'].lower() in keyword_list.lower():
                if (exclude_transfer and entry['Category'] != 'Account Transfer') or not exclude_transfer:
                    total += float(entry['Amount'])
        else:
            total += float(entry['Amount'])

    return total

# Sum expenses in given data, return total
def expenses(json_data, exclude_transfer=False):
    expense_list = []
    for entry in json_data:
        if float(entry['Amount']) < 0:
            if (exclude_transfer and entry['Category'] != 'Account Transfer') or not exclude_transfer:
                expense_list.append(entry)

    return expense_list

# Sum income in given data, return total
def income(json_data, exclude_transfer=False):
    income_list = []
    for entry in json_data:
        if float(entry['Amount']) > 0:
            if (exclude_transfer and entry['Subcategory'] != 'Account Transfer') or not exclude_transfer:
                income_list.append(entry)

    return income_list

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

    json_data = {}

    for account in accounts:
        # Possible TODO: Check if json file is already present and skip running read_csv if so
        json_data[account] = read_csv('expense_sheets/2017-05-20_' + account + '.csv', 'json_data/' + account + '.json', headers)
        print('{0}: {1}'.format(account, sum_entries(json_data[account], [])))


if __name__ == '__main__':
    main()