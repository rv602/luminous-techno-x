// Sheet and Firebase information
var scriptProperties = PropertiesService.getScriptProperties();
var sheetID = scriptProperties.getProperty('sheetID');
var firebaseUrl = scriptProperties.getProperty('firebaseUrl');
var firebaseApiKey = scriptProperties.getProperty('firebaseApiKey');

function syncEntireSheet() {
  var sheet = SpreadsheetApp.openById(sheetID).getActiveSheet();
  var data = sheet.getDataRange().getValues();
  
  var jsonData = [];

  if (data.length === 0) {
    Logger.log("Sheet is completely empty. Nothing to sync.");
    return;
  }

  // Get the headers from the first row
  var headers = data[0];

  // Find the last non-empty row in the sheet to avoid trailing empty rows
  var lastNonEmptyRow = data.length - 1;
  while (lastNonEmptyRow >= 1 && data[lastNonEmptyRow].every(cell => cell === "")) {
    lastNonEmptyRow--;
  }

  // Iterate over all rows, including potentially skipped ones
  for (var i = 1; i <= lastNonEmptyRow; i++) {
    var row = data[i] || [];  // If row is missing (e.g., empty row), use an empty array
    var rowData = {};

    // Loop through each column, ensuring keys for all columns, including empty ones
    for (var j = 0; j < headers.length; j++) {
      // Assign empty strings for any missing values
      rowData['column' + (j + 1)] = row[j] !== undefined ? row[j] : "";  
    }

    // Add the rowData to jsonData
    jsonData.push(rowData);
  }

  // Sync to Firebase
  try {
    var options = {
      'method': 'put',
      'contentType': 'application/json',
      'payload': JSON.stringify(jsonData)
    };
    
    var response = UrlFetchApp.fetch(firebaseUrl + "?auth=" + firebaseApiKey, options);
    Logger.log("Entire sheet synced to Firebase. Response: " + response.getContentText());
  } catch (error) {
    Logger.log("Error syncing to Firebase: " + error);
  }
}

function onEdit(e) {
  // Trigger a sync whenever an edit is made
  syncEntireSheet();
}

// Function to manually trigger a sync
function manualSync() {
  syncEntireSheet();
}

// Define the doGet function
function doGet(e) {
  manualSync(); // Call manualSync when a GET request is made
  return ContentService.createTextOutput("Manual sync triggered.");
}
