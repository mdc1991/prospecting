import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

pd.options.display.max_columns = 500
pd.set_option('display.width', 1000)

class SuitabilityScoreFramework:

    distance_mapping = {'London': [51.513155476370905, -0.08250200435346153],
                        'Manchester': [53.47749644768501, -2.2313297178477827],
                        'Leeds': [53.7949487438496, -1.5473966560151104],
                        'Edinburgh': [55.95203403498788, -3.1898742914884815],
                        'Birmingham': [52.4789987305319, -1.8925430714968243],
                        'Glasgow': [55.8646866939085, -4.269841378399823],
                        'Liverpool': [53.404643176974275, -2.979906679773306],
                        'Bristol': [51.46463613835566, -2.6102388779496626],
                        'Sheffield': [53.377935052438396, -1.4630209342324376],
                        'Cardiff': [51.467556049399334, -3.1667707604181947],
                        'Belfast': [54.61049723849856, -5.922107085211053],
                        'Nottingham': [52.947166321488545, -1.1474515251029],
                        'Dublin': [53.347278280585556, -6.254476908039269]
                        }
    @staticmethod
    def calculate_distances(start_location: list, end_location: list):
        """
        Calculates the distance in kms between two lat lons
        Args:
            start_location: the lat / lons of the start location
            end_location: the lat / lons of the end location

        Returns:
            the distance in km between the two
        """

        geom = [Point(xy) for xy in zip([start_location[0], end_location[0]],
                                        [start_location[1], end_location[1]]
                                        )]
        gdf = gpd.GeoDataFrame(geometry=geom, crs={'init': 'epsg:4326'})
        gdf.to_crs(epsg=3310, inplace=True)
        data_distance = gdf.distance(gdf.shift())[1]
        data_distance_km = data_distance / 1000

        return data_distance_km


    def map_all_distances(self, locations: list):
        """
        This map returns a dictionary with all the possible combinations of distances mapped out.
        It calculates the distance between the starting position and the other
        Args:
            locations: the locations from the data which need to be mapped

        Returns:
            a dictionary with each desination mapped from the starting point
        """

        all_mapped_distances = {}

        for start_city in locations:
            if start_city not in all_mapped_distances.keys():
                all_mapped_distances[start_city] = {}

            for end_city in locations:
                distance_km = self.calculate_distances(start_location=self.distance_mapping[start_city], end_location=self.distance_mapping[end_city])
                if end_city not in all_mapped_distances[start_city].keys():
                    all_mapped_distances[start_city][end_city] = distance_km

        return all_mapped_distances

    framework_weighting = {'Location': 5,
                           'Salary': 5,
                           'Skills': 3,
                           'Experience': 3,
                           'WFH': 3,
                           'Sector': 3,
                           'Area': 3,
                           'Expertise' : 5,
                           'Last Move': 3,
                           'Move Status': 5,
                           }
    sector_mapping = {
        'General Insurance - Pricing' : ['General Insurance - Pricing', 'General Insurance - Capital Modelling', 'General Insurance - Reserving'],
        'General Insurance - Capital Modelling' : ['General Insurance - Pricing', 'General Insurance - Capital Modelling', 'General Insurance - Reserving'],
        'General Insurance - Reserving' : ['General Insurance - Pricing', 'General Insurance - Capital Modelling', 'General Insurance - Reserving']
    }

    #['London Market', "Lloyd's Syndicate", 'Consultancy', 'Personal Lines', 'Commercial Lines', 'Reinsurer', 'Reinsurance Broker', 'Regulator']
    expertise_mapping = {
        'London Market': ["Lloyd's Syndicate", 'Commercial Lines', 'Reinsurer', 'Commercial Lines'],
        "Lloyd's Syndicate": ['London Market', 'Commercial Lines', 'Reinsurer', 'Commercial Lines'],
        'Consultancy': ['Broker', 'Reinsurance Broker', 'Regulator'],
        'Personal Lines': ['Regulator', 'Consultancy'],
        'Commercial Lines': ['Reinsurer', 'Reinsurance Broker', 'Regulator', 'London Market', "Lloyd's Syndicate"],
        'Reinsurer': ['Commercial Lines', 'Reinsurance Broker', "Lloyd's Syndicate", 'London Market'],
        'Broker': ['Reinsurance Broker', "Lloyd's Syndicate", 'London Market', 'Consultancy', 'Commercial Lines'],
        'Reinsurance Broker': ['Broker', "Lloyd's Syndicate", 'London Market', 'Consultancy', 'Commercial Lines'],
        'Regulator': ['Consultancy', 'Commercial Lines', 'Personal Lines']}

    def apply_framework_to_salary(self, input_salary: list, data_min_salary: int, data_max_salary: int) -> int:
        """
        This function applies the framework to the salary. Each job will be formatted with a salary range and
        this function will fit the user's chosen salary range.

        Framework:  1 if the job salary is below the minimum expected salary or 1.5x above
                    the minimum expected salary
                    2 between 1.2x and 1.5x of the expected salary
                    3 within 1.2x of the expected salary
        Args:
            input_salary: a salary range which is input from the search criteria
            data_min_salary: the minimum salary the job is paying
            data_max_salary: the maximum salary the job is paying

        Returns:
            A score of either 1, 2 or 3
        """
        input_min_salary = input_salary[0]
        input_max_salary = input_salary[1]
        high_multiplier = 1.5
        low_multiplier = 1.2

        if data_max_salary < input_min_salary or data_min_salary / input_min_salary < 1:
            return 1
        elif data_min_salary / input_min_salary <= low_multiplier:
            return 3
        elif data_min_salary / input_max_salary <= low_multiplier:
            return 2
        elif low_multiplier < data_min_salary / input_min_salary <= high_multiplier:
            return 2
        elif data_min_salary / input_max_salary >= low_multiplier:
            return 1

    def apply_framework_to_skills(self, input_skills: list, data_skills: list):
        """
        This function applies the framework to the skills. Each job will have the extracted skills within a list and
        this function will match the number of skills between user and job.

        Framework:  1 if less than 25% of skills are matched
                    2 if between 25-75% of skills are matched
                    3 if at least 75% of skills are matched

        Args:
            input_skills: The skills entered by the user
            data_skills: The skills entered / extracted for the job

        Returns:
            A score of either 1, 2, or 3

        """
        high_multipler = 0.75
        low_multiplier = 0.25

        data_skills_as_set = set(data_skills)
        if len(data_skills_as_set) == 0:
            # should raise error here or not include as should at least have skills
            # to match on
            return 1

        matched_skills = list(data_skills_as_set.intersection(input_skills))

        if len(input_skills) == 0:
            return 1

        percentage_matched = len(matched_skills) / len(data_skills_as_set)

        if percentage_matched < low_multiplier:
            return 1
        elif low_multiplier <= percentage_matched < high_multipler:
            return 2
        elif percentage_matched >= high_multipler:
            return 3

    def apply_framework_to_sector(self, input_sector: list, data_sector: str):
        """
        This framework applies the desired prospecting sectors to the candidates sector. A job may be suitable
        to someone from multiple backgrounds, e.g. pricing and reserving.

        Framework 1 - candidates discipline is not in the closest input sectors
                  2 - candidates sector is not in desired sector but in a closest sector
                  3 - candidates sector is in the desired sector
        Args:
            input_sector: a list containing the sectors of interest, e.g. [General Insurance - Pricing, General Insurance - Reserving]
            data_sector: a str with the candidates current discipline (sector)

        Returns:
            A score of 1, 2 or 3
        """
        closest_sectors = self.sector_mapping[data_sector]

        if data_sector in input_sector:
            return 3
        elif data_sector in closest_sectors:
            return 2
        else:
            return 1

    def apply_framework_to_experience_job(self, input_years: int, min_data_years: int):
        """
        This function applies the experience (in years) of the user to the minimum years required by the job.

        Framework:
            if user years <= 3
                    1 - if required years is 3 and user has 0 or 1 and > 3
                    2 - user is within 1 year of required
                    3 - user has more than or equal to number of years
            if user years  > 3
                    1 - less than 50% or over 150% of the experience required
                    2 - between 50-75% - 125-150% of experience required
                    3 - between 75% and 125% of the experience required
        Args:
            input_years: the number of years experience the user has
            min_data_years: the minimum number of years experience required by job

        Returns:
            A score of 1, 2 or 3
        """
        if input_years <= 3:
            if input_years == min_data_years:
                return 3
            elif min_data_years > 6:
                return 1
            elif input_years == 3 and min_data_years in [4, 5]:
                return 2
            elif input_years == 3 and min_data_years == 2:
                return 2
            elif input_years == 3 and min_data_years in [0, 1]:
                return 1
            elif input_years < 3:
                if np.abs(input_years - min_data_years) == 1:
                    return 2
                elif np.abs(input_years - min_data_years) > 1:
                    return 1

        experience_pct = input_years / min_data_years

        highest_pct = 1.5
        high_pct = 1.25
        low_pct = 0.75
        lowest_pct = 0.5

        if experience_pct < lowest_pct or experience_pct > highest_pct:
            return 1
        elif lowest_pct <= experience_pct < low_pct or high_pct < experience_pct <= highest_pct:
            return 2
        elif low_pct <= experience_pct <= high_pct:
            return 3

    def apply_framework_experience_prospecting(self, input_experience: list, data_experience: int):
        """
        This function applies the desired experience for the prospecting tool to the data. The input is
        the desired number of years experience of the candidate.

        Framework - 1 experience is outside 2 years of the top / bottom of the range
                    2 experience is within 2 years of top / bottom of range
                    3 experience is within desired range
        Args:
            input_experience: a list with a desired range of years experience, e.g. [3, 5] would be experience within last 3-5 years
            data_experience:  a integer value defining the number of years experience the candidate has

        Returns:
                A score of 1, 2 or 3
        """

        min_input_experience = input_experience[0]
        max_input_experience = input_experience[1]
        input_experience_range = [x for x in range(min_input_experience, max_input_experience + 1)]

        min_input_experience_m2 = max(0, min_input_experience - 2)
        max_input_experience_m2 = max_input_experience + 2
        input_experience_range_m2 = [x for x in range(min_input_experience_m2, max_input_experience_m2 + 1)]

        if data_experience in input_experience_range:
            return 3
        elif data_experience in input_experience_range_m2:
            return 2
        else:
            return 1

    def apply_framework_to_last_moved(self, input_moved: list, data_moved: int):
        """
        This function applies the desired last moved date for the prospecting tool to the data. The input is
        the desired last moved date of the candidate.

        Framework - 1 data_moved is outside 2 years of the top / bottom of the range
                    2 data is within 2 years of top / bottom of range
                    3 data is within desired range
        Args:
            input_moved: a list with a desired range of move dates, e.g. [3, 5] would be moved within last 3-5 years
            data_moved:  a integer value defining the number of years since candidate last moved

        Returns:
                A score of 1, 2 or 3
        """

        min_input_moved = input_moved[0]
        max_input_moved = input_moved[1]
        input_moved_range = [x for x in range(min_input_moved, max_input_moved + 1)]

        min_input_moved_m2 = max(0, min_input_moved - 2)
        max_input_moved_m2 = max_input_moved + 2
        input_moved_range_m2 = [x for x in range(min_input_moved_m2, max_input_moved_m2 + 1)]

        if data_moved in input_moved_range:
            return 3
        elif data_moved in input_moved_range_m2:
            return 2
        else:
            return 1

    def apply_framework_to_wfh(self, input_wfh: list, data_wfh: int):
        """
        This function applies the framework to the number of days the user wishes to work from home (WFH).
        The number of days is x or more, e.g. the user will input 2 for 2 or more days WFH or 4 for
        4 or more days wfh.

        Args:
            input_wfh: at least this number of days working from home
            data_wfh: number of days offered by the job

        Returns:
            A score of 1, 2 or 3
        """
        input_wfh_min = input_wfh[0]

        if data_wfh == 0 and input_wfh_min > 0:
            return 1
        elif data_wfh in input_wfh:
            return 3
        elif data_wfh > max(input_wfh):
            if np.abs(max(input_wfh) - data_wfh) == 1:
                return 2
            elif np.abs(max(input_wfh) - data_wfh) > 1:
                return 1
        elif data_wfh < min(input_wfh):
            if np.abs(min(input_wfh) - data_wfh) == 1:
                return 2
            elif np.abs(min(input_wfh) - data_wfh) > 1:
                return 1

    def apply_framework_location(self, input_location: str, data_location: str, all_mapped_distances: dict):
        """
        This function applies the framework to the job locations. The closer the job location to the users
        preferred location the higher the score given.

        Framework:
                1 - Job over 100km away
                2 - Job between 50-100km away
                3 - Job within 50km away
        Args:
            input_location: the desired location of the candidates job
            data_location: the location of the job
            all_mapped_distances: a dictionary containing the mapped start and end locations

        Returns:
            A score of 1, 2 or 3
        """

        data_distance_km = all_mapped_distances[input_location][data_location]

        if data_distance_km <= 50:
            return 3
        elif data_distance_km <= 100:
            return 2
        else:
            return 1

    def apply_framework_to_areas(self, input_areas: list, data_areas: list):
        """
        This function applies the framework to the areas of experience which the recruiter is looking for

        Framework - 1 - if less than 50% of areas match
                    2 - if 50-75% of areas match
                    3 - if 75% to 100% of areas match
        Args:
            input_areas: a list of areas which the recruiter would like experience in
            data_areas: a list of areas which the candidate has experience in

        Returns:
            A score of 1, 2 or 3
        """

        matched_skills = list(set(data_areas).intersection(input_areas))
        matched_pct = len(matched_skills) / len(input_areas)
        min_percentage = 0.5
        max_percentage = 0.75
        if matched_pct >= max_percentage:
            return 3
        elif min_percentage <= matched_pct < max_percentage:
            return 2
        elif matched_pct < min_percentage:
            return 1

    def apply_framework_to_area_of_expertise(self, input_expertise: str, data_expertise: str):
        """
        This function applies the framework to the single area of expertise of the candidate.

        Framework 1 - if candidate has area of expertise outside of similar areas
                  2 - if candidate has similar experience to area of expertise
                  3 - if candidate's area of expertise is equal to search criteria

        Args:
            input_expertise: the search criteria for area of expertise
            data_expertise: the area of expertise of the candidate

        Returns:
            A score of 1, 2 or 3
        """

        closest_areas_of_expertise = self.expertise_mapping[data_expertise]

        if data_expertise in input_expertise:
            return 3
        elif data_expertise in closest_areas_of_expertise:
            return 2
        else:
            return 1

    def apply_framework_to_move_status(self, input_move_status: list, data_move_status: str):
        """
        This framework is for a recruiter searching for matching jobs. A candidate could be either
        Actively Looking, Open Minded, Unlikely to Move or Not Available

        Framework - 1 if data_move_status is outside of the closest move statuses
                    2 if data_move_status is within the closest move statuses but not within actual search
                    3 if data_move_status is within the search criteria
        Args:
            input_move_status: a list of move statuses which the recruiter wishes to search
            data_move_status: the move status of the candidate

        Returns:
            returns a score of 1, 2 or 3
        """

        if data_move_status in input_move_status:
            return 3
        elif 'Urgently Looking' in input_move_status and data_move_status in ['Actively Looking']:
            return 2
        elif 'Actively Looking' in input_move_status and data_move_status in ['Urgently Looking', 'Open Minded']:
            return 2
        elif 'Open Minded' in input_move_status and data_move_status in ['Actively Looking']:
            return 2
        else:
            return 1

    def apply_framework(self, **kwargs) -> float:
        """
        This function applies the framework to a particular set of scores. Designed to be used as
        .apply(lambda r: apply_framework(r[score_col], r[...], ...), axis=1)

        Args:
            salary_score: the score between 1 and 3 for salary, after the framework has been applied
            skills_score: the score between 1 and 3 for skills, after the framework has been applied
            experience_score: the score between 1 and 3 for experience, after the framework has been applied
            wfh_score: the score between 1 and 3 for wfh, after the framework has been applied
            location_score: the score between 1 and 3 for location, after the framework has been applied

        Returns:
            A score between 0-100 representing the suitability score of the job to the candidate or the
            candidate to the job search
        """
        kwargs_to_framework_mapping = {'salary_score': 'Salary',
                                       'skills_score': 'Skills',
                                       'experience_score': 'Experience',
                                       'wfh_score': 'WFH',
                                       'location_score': 'Location',
                                       'sector_score': 'Sector',
                                       'area_score': 'Area',
                                       'expertise_score': 'Expertise',
                                       'move_score': 'Last Move',
                                       'status_score': 'Move Status'}

        all_frameworks = list(kwargs_to_framework_mapping[x] for x in kwargs.keys())
        framework_scores = list(kwargs.values())

        score_check = any([True if x else False for x in framework_scores])

        if score_check:
            weightings = [self.framework_weighting[x] for x in all_frameworks]
            max_available_score = sum([x * 3 for x in weightings])
            min_available_score = sum([x * 1 for x in weightings])
            denominator = max_available_score - min_available_score

            weighted_score = sum([x * y for x, y in zip(framework_scores, weightings)])

            suitability_score = int(np.round(((weighted_score - min_available_score) / denominator) * 100, 0))

            return suitability_score






