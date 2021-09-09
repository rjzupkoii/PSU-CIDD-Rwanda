/*
 * rwa_rainfall_gee.js
 *
 * Google Earth Engine script that uses the ERA5 monthly aggregates to calculate 
 * the mean rainfall for each month in the area of interest.
 */

// Prepare the imagery data
var era5 = ee.ImageCollection("ECMWF/ERA5/MONTHLY");

// Define an area of interest
var aoi = ee.Geometry.Rectangle([28.8482, -2.8581,  30.9158, -1.0466], null, false);

// Define the filter for the distinct months
var distinctYear = era5.distinct('month');
var filter = ee.Filter.equals({leftField: 'month', rightField: 'month'});
var join = ee.Join.saveAll('sameMonth');

// Generate a collection with labeled months
var collection = ee.ImageCollection(join.apply(distinctYear, era5, filter));
collection = collection.map(function(image) {
  var year = ee.ImageCollection.fromImages(image.get('sameMonth'));
  return year.mean().set('Month', image.get('month'));
});

// Convert from meters to centimeters
var collection = collection.map(function(image) {
  var rainfall = image.select(['total_precipitation'], ['total_precipitation_cm']).multiply(100.0);
  return image.addBands(rainfall);
});

// Calculate the mean monthly rainfall
var rainfall = collection.map(function(image) {
  var reduce = image.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: aoi,
    scale: 10000
  });  
  return ee.Feature(aoi, reduce).set('Month', image.get('Month'));
});

// Add the AOI bounds as a quality check
Map.centerObject(aoi, 8);
Map.addLayer(aoi, null, 'Area of Interest');

// Generate the rainfall chart
print(ui.Chart.feature.byFeature({
  features: rainfall,
  xProperty: 'Month',
  yProperties: ['total_precipitation_cm']
}).setOptions({
  title: 'Mean monthly rainfall (cm)',
  legend: { position: 'none' },
  hAxis: { 
    title: 'Month', 
    ticks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  },
  vAxis: { title: 'Rainfall (cm)' }
}));

// Queue the Google Drive export
var values = rainfall.aggregate_array('total_precipitation_cm');
values = ee.FeatureCollection(values.map(function(value) {
  return ee.Feature(null, {'rainfall': value});
}));
Export.table.toDrive({
  collection: values,
  description: 'EE_Rainfall_Export',
  folder: 'Earth Engine',
  fileNamePrefix: 'rwa_rainfall',
  fileFormat: 'CSV'
});