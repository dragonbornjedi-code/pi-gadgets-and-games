#!/usr/bin/env python3
"""
PHASE 5: Full Simulation Test for all 42 combinations (7 modes × 6 difficulties)
Tests without display requirement (uses SDL_VIDEODRIVER=dummy).
Exit code 0 only if all 42 pass. Exit code 1 with summary if any fail.
"""

import os
import sys
import random

# Headless display mode
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

sys.path.insert(0, '.')

import pygame
from framework.gamestate.game_modes import SimonSaysSession, GameMode, Difficulty, MODE_CONFIG
from framework.input.input_manager import InputManager

pygame.init()
pygame.display.set_mode((480, 320))

# Test data
results = {
    "passed": 0,
    "failed": 0,
    "failures": [],
}

COMBINATIONS = [
    (GameMode.MEMORY_STANDARD, Difficulty.BEGINNER),
    (GameMode.MEMORY_STANDARD, Difficulty.INTERMEDIATE),
    (GameMode.MEMORY_STANDARD, Difficulty.HARD),
    (GameMode.MEMORY_STANDARD, Difficulty.EXPERT),
    (GameMode.MEMORY_STANDARD, Difficulty.CHAMPION),
    (GameMode.MEMORY_STANDARD, Difficulty.GRAND_MASTER),
    
    (GameMode.MEMORY_BACKWARDS, Difficulty.BEGINNER),
    (GameMode.MEMORY_BACKWARDS, Difficulty.INTERMEDIATE),
    (GameMode.MEMORY_BACKWARDS, Difficulty.HARD),
    (GameMode.MEMORY_BACKWARDS, Difficulty.EXPERT),
    (GameMode.MEMORY_BACKWARDS, Difficulty.CHAMPION),
    (GameMode.MEMORY_BACKWARDS, Difficulty.GRAND_MASTER),
    
    (GameMode.SPEED_ATTACK, Difficulty.BEGINNER),
    (GameMode.SPEED_ATTACK, Difficulty.INTERMEDIATE),
    (GameMode.SPEED_ATTACK, Difficulty.HARD),
    (GameMode.SPEED_ATTACK, Difficulty.EXPERT),
    (GameMode.SPEED_ATTACK, Difficulty.CHAMPION),
    (GameMode.SPEED_ATTACK, Difficulty.GRAND_MASTER),
    
    (GameMode.ENDURANCE_STANDARD, Difficulty.BEGINNER),
    (GameMode.ENDURANCE_STANDARD, Difficulty.INTERMEDIATE),
    (GameMode.ENDURANCE_STANDARD, Difficulty.HARD),
    (GameMode.ENDURANCE_STANDARD, Difficulty.EXPERT),
    (GameMode.ENDURANCE_STANDARD, Difficulty.CHAMPION),
    (GameMode.ENDURANCE_STANDARD, Difficulty.GRAND_MASTER),
    
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.BEGINNER),
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.INTERMEDIATE),
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.HARD),
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.EXPERT),
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.CHAMPION),
    (GameMode.ENDURANCE_BACKWARDS, Difficulty.GRAND_MASTER),
    
    (GameMode.MASTER_CHALLENGE, Difficulty.BEGINNER),
    (GameMode.MASTER_CHALLENGE, Difficulty.INTERMEDIATE),
    (GameMode.MASTER_CHALLENGE, Difficulty.HARD),
    (GameMode.MASTER_CHALLENGE, Difficulty.EXPERT),
    (GameMode.MASTER_CHALLENGE, Difficulty.CHAMPION),
    (GameMode.MASTER_CHALLENGE, Difficulty.GRAND_MASTER),
    
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.BEGINNER),
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.INTERMEDIATE),
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.HARD),
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.EXPERT),
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.CHAMPION),
    (GameMode.MASTER_REVERSE_CHALLENGE, Difficulty.GRAND_MASTER),
]

def simulate_round(session, round_num):
    """Simulate a single round with correct button inputs."""
    try:
        # Start playback
        session.phase = "showing"
        session.playback_active = True
        session.playback_index = 0
        session.playback_frame = 0
        
        # Simulate playback (fast-forward)
        while session.playback_active and not session.failed:
            session.update({"button_down": []}, 0.05)
        
        if session.failed:
            return False, f"Failed during playback: {session.failure_reason}"
        
        # Now simulate correct input
        if session.phase != "input":
            return False, f"Phase not 'input' after playback (got '{session.phase}')"
        
        # Get correct sequence (considering backwards modes)
        correct_seq = session.sequence
        if session.mode in (GameMode.MEMORY_BACKWARDS, GameMode.ENDURANCE_BACKWARDS, 
                            GameMode.MASTER_REVERSE_CHALLENGE):
            correct_seq = session.sequence[::-1]
        
        # Input buttons one by one
        for button in correct_seq:
            input_data = {"button_down": [button]}
            session.update(input_data, 0.05)
            
            if session.failed:
                return False, f"Failed on correct input: {session.failure_reason}"
        
        if not session.completed and session.round_count < session.config.max_rounds:
            # Round should continue if not at max
            if session.phase != "showing":
                return False, f"Phase should be 'showing' after round (got '{session.phase}')"
            if len(session.sequence) <= 3 and session.config.grows_sequence:
                # Check sequence growth
                return True, None
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_combination(mode, difficulty):
    """Test a single mode/difficulty combination."""
    try:
        session = SimonSaysSession(mode, difficulty)
    except Exception as e:
        return False, f"Failed to initialize: {e}"
    
    # Verify initial state
    if not session.sequence or len(session.sequence) == 0:
        return False, "Empty sequence after initialization"
    
    if session.score != 0:
        return False, f"Initial score not 0 (got {session.score})"
    
    if session.completed or session.failed:
        return False, "Session already completed/failed after init"
    
    # Simulate 3 complete rounds
    for round_num in range(1, 4):
        success, error = simulate_round(session, round_num)
        if not success:
            return False, f"Round {round_num}: {error}"
        
        # Verify score incremented
        if session.score <= 0:
            return False, f"Score not incremented after round {round_num}"
    
    # For backwards modes: verify reversed input accepted, forward rejected
    if mode in (GameMode.MEMORY_BACKWARDS, GameMode.ENDURANCE_BACKWARDS, GameMode.MASTER_REVERSE_CHALLENGE):
        session = SimonSaysSession(mode, difficulty)
        session.phase = "input"
        
        # The correct button is the FIRST button of the REVERSED sequence
        correct_button = session.sequence[::-1][0]
        
        # The wrong button would be the forward first button
        wrong_button = session.sequence[0]
        
        # Only test if they're different (otherwise test is meaningless)
        if wrong_button != correct_button:
            # Try forward input (should fail)
            session_test = SimonSaysSession(mode, difficulty)
            session_test.phase = "input"
            input_data = {"button_down": [wrong_button]}
            session_test.update(input_data, 0.05)
            
            if not session_test.failed:
                return False, "Forward input should fail in backwards mode"
        
        # Verify reversed input works
        session = SimonSaysSession(mode, difficulty)
        session.phase = "input"
        reversed_button = session.sequence[::-1][0]
        input_data = {"button_down": [reversed_button]}
        session.update(input_data, 0.05)
        
        if session.failed:
            return False, f"Reversed input failed: {session.failure_reason}"
    
    # For timed modes: verify timer decrements
    if mode in (GameMode.SPEED_ATTACK, GameMode.ENDURANCE_STANDARD, GameMode.ENDURANCE_BACKWARDS,
                GameMode.MASTER_CHALLENGE, GameMode.MASTER_REVERSE_CHALLENGE):
        session = SimonSaysSession(mode, difficulty)
        initial_time = session.time_remaining
        session.update({"button_down": []}, 0.5)
        
        if session.time_remaining >= initial_time:
            return False, f"Timer not decremented in timed mode"
    
    # For grows_sequence modes: verify sequence growth
    if mode in (GameMode.MEMORY_STANDARD, GameMode.MEMORY_BACKWARDS, GameMode.MASTER_CHALLENGE,
                GameMode.MASTER_REVERSE_CHALLENGE):
        session = SimonSaysSession(mode, difficulty)
        seq1_len = len(session.sequence)
        
        # Simulate complete round to trigger growth
        session.phase = "input"
        for button in session.sequence:
            session.update({"button_down": [button]}, 0.05)
        
        if session.round_count >= 1:
            seq2_len = len(session.sequence)
            if seq2_len != seq1_len + 1:
                return False, f"Sequence growth failed: {seq1_len} → {seq2_len} (expected {seq1_len + 1})"
    
    # For Master modes: verify timer reward
    if mode in (GameMode.MASTER_CHALLENGE, GameMode.MASTER_REVERSE_CHALLENGE):
        session = SimonSaysSession(mode, difficulty)
        session.phase = "input"
        
        # Set time to reasonable value for reward testing
        session.time_remaining = 10.0
        initial_time = session.time_remaining
        
        # Input correct sequence
        correct_seq = session.sequence if mode == GameMode.MASTER_CHALLENGE else session.sequence[::-1]
        for button in correct_seq:
            session.update({"button_down": [button]}, 0.05)
        
        if session.round_count >= 1:
            if session.time_remaining <= initial_time:
                return False, f"Timer reward not applied in Master mode"
    
    # For Grand Master: verify combo_ready flag
    if difficulty == Difficulty.GRAND_MASTER:
        session = SimonSaysSession(mode, difficulty)
        config = session.config
        if not config.enable_combos:
            return False, f"enable_combos not set for Grand Master"
    
    return True, None

def main():
    print("\n" + "="*60)
    print("PHASE 5: FULL SIMULATION TEST - ALL 42 COMBINATIONS")
    print("="*60 + "\n")
    
    for i, (mode, difficulty) in enumerate(COMBINATIONS, 1):
        combo_name = f"{mode.value} + {difficulty.value}"
        print(f"[{i:2d}/42] {combo_name:<45}", end=" ", flush=True)
        
        passed, error = test_combination(mode, difficulty)
        
        if passed:
            print("✓ PASS")
            results["passed"] += 1
        else:
            print(f"✗ FAIL")
            results["failed"] += 1
            results["failures"].append((combo_name, error))
    
    # Summary
    print("\n" + "="*60)
    print(f"RESULTS: {results['passed']}/42 passed, {results['failed']}/42 failed")
    print("="*60)
    
    if results["failed"] > 0:
        print("\nFAILURES:")
        for combo, error in results["failures"]:
            print(f"  ✗ {combo}")
            print(f"    → {error}")
        print()
        return 1
    else:
        print("\n✅ ALL 42 COMBINATIONS PASSED!\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
