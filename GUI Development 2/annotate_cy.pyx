import cv2

def annotate_raw_image(frame, annotation_settings, exposure_time, loop_count, elapsed_time, fps):
    annotated_frame = frame
    frame_height, frame_width, _ = annotated_frame.shape

    ### ─── TOP LEFT ───────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("top-left"):
        line_offset = 0
        top_left_start_y = 30
        spacing = 20

        # Exposure Time
        cv2.putText(annotated_frame, f"ET: {exposure_time}", (10, top_left_start_y + spacing * line_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        line_offset += 1

        # Time
        if annotation_settings["manual_settings"]["top_left_fields"]["Time"].get("show"):
            text = round(elapsed_time,2)
            cv2.putText(annotated_frame, f"Time: {text}", (10, top_left_start_y + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # FA
        if annotation_settings["manual_settings"]["top_left_fields"]["FA"].get("show"):
            text = annotation_settings["manual_settings"]["top_left_fields"]["FA"].get("value")
            cv2.putText(annotated_frame, f"FA: {text}", (10, top_left_start_y + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    ### ─── TOP RIGHT ──────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("top-right"):
        line_offset = 0
        top_right_start_y = 30
        spacing = 20

        fields = annotation_settings["manual_settings"]["top_right_fields"]
        if fields["FPS"].get("show"):
            text = str(round(fps,2))
            cv2.putText(annotated_frame, "FPS: " + text,
                        (frame_width - 235, top_right_start_y + spacing * line_offset ),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1
            
        if fields["Running"].get("show"):
            text = "Basler UI"
            cv2.putText(annotated_frame, "Running: " + text,
                        (frame_width - 235, top_right_start_y + spacing * line_offset ),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1
            
        if fields["Output"].get("show"):
            text = "Sample"
            cv2.putText(annotated_frame, "Output: " + text,
                        (frame_width - 235, top_right_start_y + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1
            
        for field in ["Illum", "Shielding Gas", "Note"]:
            if fields[field].get("show"):
                text = f"{field}: {fields[field].get('value')}"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.putText(annotated_frame, text,
                            (frame_width - 235, top_right_start_y + spacing * line_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                line_offset += 1

    ### ─── BOTTOM LEFT ────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("bottom-left"):
        line_offset = 0
        bottom_left_start_y = frame_height - 100
        spacing = 20

        fields = annotation_settings["manual_settings"]["bottom_left_fields"]
        for field in ["Material", "Job Number", "Wire Feed Speed", "Travel Speed"]:
            if fields[field].get("show"):
                text = f"{field}: {fields[field].get('value')}"
                cv2.putText(annotated_frame, text,
                            (10, bottom_left_start_y + spacing * line_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                line_offset += 1

    ### ─── BOTTOM RIGHT ───────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("bottom-right"):
        line_offset = 0
        bottom_right_start = frame_height - 120
        spacing = 20

        # Camera
        if annotation_settings["manual_settings"]["bottom_right_fields"]["Camera"].get("show"):
            text = annotation_settings["manual_settings"]["bottom_right_fields"]["Camera"].get("value")
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Lens + Viewing Angle
        fields = annotation_settings["manual_settings"]["bottom_right_fields"]
        show_lens = fields["Lens"].get("show")
        show_angle = fields["Viewing Angle"].get("show")
        lens_val = fields["Lens"].get("value")
        angle_val = fields["Viewing Angle"].get("value")

        if show_lens or show_angle:
            combined = []
            if show_lens:
                combined.append(lens_val)
            if show_angle:
                combined.append(angle_val)
            text = " | ".join(combined)
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Focus
        if fields["Focus"].get("show") & fields["Aperature"].get("show"):
            cv2.putText(annotated_frame, "F:" + fields["Focus"].get("value") + " | A:" + fields["Aperature"].get("value"),
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1
        elif fields["Focus"].get("show"):
            cv2.putText(annotated_frame, "F:" + fields["Focus"].get("value"),
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Aperture (note: JSON typo was "Aperature" but use "Aperture" for consistency)
        
            
        elif fields["Aperature"].get("show"):
            cv2.putText(annotated_frame, "A:" + fields["Aperature"].get("value"),
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Distance
        if fields["Distance"].get("show"):
            text = f"Distance: {fields['Distance'].get('value')}"
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # CTWD
        if fields["CTWD (mm)"].get("show"):
            text = f"dNtW (mm): {fields['CTWD (mm)'].get('value')}"
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return annotated_frame

def update_camera_status(object status_label, str state, str detail=""):
    """
    Updates the passed-in label based on the current state.
    """
    cdef dict status_mapping = {
        'idle': ("Idle", "yellow"),
        'recording': ("Recording", "green"),
        'waiting_rsi': ("Waiting for RSI", "blue"),
        'tolerance_error': ("Out of Tolerance", "red"),
    }

    if state not in status_mapping:
        print(f"⚠️ Unknown status: {state}")
        return

    status_text, status_color = status_mapping[state]

    if detail:
        status_text += f"\n{detail}"

    status_label.configure(text=status_text, text_color=status_color)
