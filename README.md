# Signatures in Shape analysis: An Efficient Approach to Motion Identification

This repository contains the framework used for the master thesis with the same
title. This project will also be published in the conference
proceedings for the GSI 2019 conferencce.

# Project structure

## Animation

The animation folder contains two subfolders: src and db. 

```src/``` contains all things animation related, that is Skeleton and Animation objects,
methods for parsing .asf/.amc-files, methods for creating animations and some
attempts at different frame interpolation.

```db/``` contains data and our database. To create the tables run:

```sqlite3 <Name_of_db>.db < create_tables_sqlite3.sql```


Download and unzip the mocap data, which can be obtained from http://mocap.cs.cmu.edu


create config-file: ```cp db_config_example.py db_config.py```

and add the paths to your database and subject folder.

run:

``` python insert_data_db_sqllite3.py```

to add data to database and download subject descriptions from mocap.cs.cmu.edu

```animation_manager.py``` is an interface for fetching animations in
applications

## so3

The folder so3/ contains implementation our mathematical framework for SO3.

```convert.py``` : convert animation to curce in SO3.

```transformations.py``` log, exp, interpolate, SRVT and other transformations
applied to SO3 or curves in SO3.

```curves.py```: operations that take a curve, or multiple curves as
parameters. This includes distance, dynamic_distance, close, move_origin and
others. These are all written to be functional in style.

```dynamic_distance.py```: implementations off the the dynamic distance method
proposed by Bauer.

```signature.py and log_signature.py```: proposed metrics, calculated for
geodesic interpolation curves using the iisignature library.


the folders ```experiments/``` and ```clustering/``` contain different
applications of these methods.  

## se3

Transformations applied to the group SE(3), the above mentioned framework could
be applied to this group using a similar approach.

