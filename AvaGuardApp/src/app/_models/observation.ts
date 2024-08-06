export class Observation {
    observation_id?: string;
    datetime_taken_UTC?: Date;
    timestamp_saved?: Date;
    imagefile_url?: string;
    observation_notes?: string;
    avalanche_triggered?: boolean;
    avalanche_observed?: boolean;
    avalanche_experienced?: boolean;
    avalanche_flag?: boolean;
    cracking?: boolean;
    collapsing?: boolean;
    elevation_type?: string;
    lat?: number = 0;
    lng?: number= 0;
    general_location?: string;
    submitted_user?: string;
    marked_for_deletion?: boolean;
    terrain_prediction_score?: number;
    avalanche_prediction_score?: number;
    avalanche_category_prediction?: number;
    segmented_image_url?: string;
}