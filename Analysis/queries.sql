-- Basic monitoring query
select c.id as configurationid, filename, replicateid, 
  starttime, now() - starttime as runningtime, 
  max(dayselapsed) as modeldays
from sim.replicate r
  inner join sim.configuration c on c.id = r.configurationid
  inner join sim.monthlydata md on md.replicateid = r.id
where r.endtime is null
group by c.id, filename, replicateid, starttime
order by modeldays desc

-- Status of all replicates
select configurationid, studyid, filename, 
  sum(complete) as complete,
  count(id) as total
from (
select c.id as configurationid, c.studyid, c.filename,
  r.id,
  case when r.endtime is null then 0 else 1 end as complete
from sim.configuration c
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid > 2) iq
group by configurationid, studyid, filename
order by studyid, filename

-- General aggergation query for 561H replicates at the district level
select c.id as configurationid,
  sd.replicateid,
  sd.dayselapsed,
  sd.district,
  infectedindividuals, 
  clinicalepisodes, 
  case when gd.clinicaloccurrences is null then 0 else gd.clinicaloccurrences end as clinicaloccurrences,
  case when gd.weightedoccurrences is null then 0 else gd.weightedoccurrences end as weightedoccurrences
from (
  select md.replicateid, md.dayselapsed, msd.location as district,
    sum(msd.infectedindividuals) as infectedindividuals, 
    sum(msd.clinicalepisodes) as clinicalepisodes
  from sim.monthlydata md
    inner join sim.monthlysitedata msd on msd.monthlydataid = md.id
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
  group by md.replicateid, md.dayselapsed, msd.location) sd
left join (
  select md.replicateid, md.dayselapsed, mgd.location as district,
    sum(mgd.clinicaloccurrences) as clinicaloccurrences,
    sum(mgd.weightedoccurrences) as weightedoccurrences
  from sim.monthlydata md
    inner join sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    inner join sim.genotype g on g.id = mgd.genomeid
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
    and g.name ~ '^.....H.'
  group by md.replicateid, md.dayselapsed, mgd.location) gd 
  	on (gd.replicateid = sd.replicateid 
	  and gd.dayselapsed = sd.dayselapsed
	  and gd.district = sd.district)
inner join sim.replicate r on r.id = sd.replicateid
inner join sim.configuration c on c.id = r.configurationid
where r.endtime is not null
  and c.studyid = 4
order by replicateid, dayselapsed

-- General aggergation query for 561H validation replicates at the district level
select c.id as configurationid,
  sd.replicateid,
  sd.dayselapsed,
  sd.district,
  infectedindividuals, 
  clinicalepisodes, 
  case when gd.clinicaloccurrences is null then 0 else gd.clinicaloccurrences end as clinicaloccurrences,
  case when gd.weightedoccurrences is null then 0 else gd.weightedoccurrences end as weightedoccurrences
from (
  select md.replicateid, md.dayselapsed, msd.location as district,
    sum(msd.infectedindividuals) as infectedindividuals, 
    sum(msd.clinicalepisodes) as clinicalepisodes
  from sim.monthlydata md
    inner join sim.monthlysitedata msd on msd.monthlydataid = md.id
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
  group by md.replicateid, md.dayselapsed, msd.location) sd
left join (
  select md.replicateid, md.dayselapsed, mgd.location as district,
    sum(mgd.clinicaloccurrences) as clinicaloccurrences,
    sum(mgd.weightedoccurrences) as weightedoccurrences
  from sim.monthlydata md
    inner join sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    inner join sim.genotype g on g.id = mgd.genomeid
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
    and g.name ~ '^.....H.'
  group by md.replicateid, md.dayselapsed, mgd.location) gd 
  	on (gd.replicateid = sd.replicateid 
	  and gd.dayselapsed = sd.dayselapsed
	  and gd.district = sd.district)
inner join sim.replicate r on r.id = sd.replicateid
inner join sim.configuration c on c.id = r.configurationid
where r.endtime is not null
  and c.id = 4025
order by replicateid, dayselapsed

-- View to select 561H replicates and configurations from
CREATE VIEW v_561h_replicates AS
SELECT c.id AS configurationid, c.filename, r.id AS replicateid, c.studyid
FROM sim.configuration c
  INNER JOIN sim.replicate r ON r.configurationid = c.id
WHERE c.studyid > 2