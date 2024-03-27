        <div class="turn-container">
            Turn: <span id="turn-count">{{ turn_count }}</span>
            <form id="pass-turn-form" class="pass-turn-form">
                <button type="button" id="pass-turn-btn">Pass Turn</button>
            </form>
        </div>

        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            $(document).ready(function() {
                $('#pass-turn-btn').click(function(e) {
                    e.preventDefault();
                    $.ajax({
                        url: '/pass_turn',
                        type: 'POST',
                        success: function(response) {
                            // Log the response for debugging
                            console.log(response);
                            // Update the turn count with the new value
                            $('#turn-count').text(response.turn_count);
                        },
                        error: function(xhr, status, error) {
                            console.error('Error:', error);
                            // Log detailed error information for debugging
                            console.log(xhr);
                            console.log(status);
                        }
                    });
                });
            });
        </script>