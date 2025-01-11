$(document).ready(function() {
    let searchTimeout = null;
    const $communitySearch = $('#communitySearch');
    const $communityResults = $('#communityResults');
    const $communityId = $('#communityId');
    const $selectedCommunity = $('#selectedCommunity');
    
    // Initialize with pre-selected community if available
    if (window.preSelectedCommunity) {
        $communityId.val(window.preSelectedCommunity.id);
        $communitySearch.val(window.preSelectedCommunity.name);
        $selectedCommunity.text(`Selected community: ${window.preSelectedCommunity.name}`);
    }
    
    // Style the results dropdown
    $communityResults.css({
        'position': 'absolute',
        'z-index': '1000',
        'width': $communitySearch.outerWidth(),
        'max-height': '200px',
        'overflow-y': 'auto',
        'background': '#fff',
        'border': '1px solid rgba(0,0,0,.125)',
        'border-radius': '0.25rem',
        'box-shadow': '0 2px 4px rgba(0,0,0,.1)'
    });

    $communitySearch.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();
        
        if (query.length < 2) {
            $communityResults.addClass('d-none').html('');
            $selectedCommunity.text('');
            return;
        }

        $selectedCommunity.text('Searching...');
        
        searchTimeout = setTimeout(() => {
            $.ajax({
                url: '../BackEnd/search_community.php',
                method: 'GET',
                data: { query: query },
                success: function(response) {
                    if (response.success && response.data.length > 0) {
                        $communityResults.removeClass('d-none').html(
                            response.data.map(community => `
                                <a href="#" class="list-group-item list-group-item-action community-item" 
                                   data-id="${community.id}" 
                                   data-name="${community.name}">
                                    <strong>${community.name}</strong>
                                </a>
                            `).join('')
                        );
                        $selectedCommunity.text('');
                    } else {
                        $communityResults.addClass('d-none');
                        $selectedCommunity.text('No communities found');
                    }
                },
                error: function() {
                    $communityResults.addClass('d-none');
                    $selectedCommunity.text('Error searching communities');
                }
            });
        }, 300);
    });

    // Close results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.community-search-wrapper').length) {
            $communityResults.addClass('d-none');
        }
    });

    // Handle keyboard navigation
    $communitySearch.on('keydown', function(e) {
        const $items = $communityResults.find('.community-item');
        const $focused = $communityResults.find('.focused');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (!$focused.length) {
                    $items.first().addClass('focused');
                } else {
                    $focused.removeClass('focused').next().addClass('focused');
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if ($focused.length) {
                    $focused.removeClass('focused').prev().addClass('focused');
                }
                break;
            case 'Enter':
                e.preventDefault();
                if ($focused.length) {
                    $focused.click();
                }
                break;
        }
    });

    $communityResults.on('click', '.community-item', function(e) {
        e.preventDefault();
        const id = $(this).data('id');
        const name = $(this).data('name');
        
        $communityId.val(id);
        $communitySearch.val(name);
        $selectedCommunity.text(`Selected community: ${name}`);
        $communityResults.addClass('d-none').html('');
    });

    $('#clearCommunity').click(function() {
        $communityId.val('');
        $communitySearch.val('');
        $selectedCommunity.text('');
    });
});
