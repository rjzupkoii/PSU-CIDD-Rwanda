/*
 * rwa_era5_rainfall_doy.js
 *
 * Google Earth Engine script that uses the ERA5 daily aggregates to calculate 
 * the mean rainfall for each day of the year in the area of interest.
 */

// Prepare the imagery data
var era5 = ee.ImageCollection("ECMWF/ERA5/DAILY");

// Define an area of interest
var country = ee.FeatureCollection("FAO/GAUL/2015/level0")
  .filter(ee.Filter.eq('ADM0_NAME', 'Rwanda'));
var aoi = ee.Feature(country.first().set('geo_type', 'Polygon')).geometry();

// Filter to the years that we are interested in, drop leap days to keep things consisent
var collection = ee.ImageCollection(
  era5.filterDate('2009-01-01', '2019-12-31')
    .filter(ee.Filter.and(ee.Filter.eq('month', 2), ee.Filter.eq('day', 29)).not()));

// Append the day of year to the properties, note the day of year is adjusted for leap years
collection = collection.map(function(image) {
  var doy = image.date().getRelative('day', 'year');
  doy = ee.Number.expression('(doy > 58 && year % 4 == 0) ? doy - 1 : doy', {year : image.get('year'), doy : doy});
  return image.set('doy', doy);
});

// Join on the distinct day of year and calculate the mean
var distinctDOY = collection.distinct('doy');
var filter = ee.Filter.equals({leftField: 'doy', rightField: 'doy'});
var join = ee.Join.saveAll('sameDOY');
collection = ee.ImageCollection(join.apply(distinctDOY, collection, filter));
collection = collection.map(function(image) {
  var year = ee.ImageCollection.fromImages(image.get('sameDOY'));
  return year.mean().set('DOY', image.get('doy'));
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
  return ee.Feature(aoi, reduce).set('DOY', image.get('DOY'));
});

// Add the AOI bounds as a quality check
Map.centerObject(aoi, 6);
Map.addLayer(aoi, {}, 'Country Boundaries');

// Generate the rainfall chart
print(ui.Chart.feature.byFeature({
  features: rainfall,
  xProperty: 'DOY',
  yProperties: ['total_precipitation_cm']
}).setOptions({
  title: 'Mean monthly rainfall (cm)',
  legend: { position: 'none' },
  vAxis: { title: 'Rainfall (cm)' },
  hAxis: { title: 'Day of Year' }
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