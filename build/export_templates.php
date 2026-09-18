<?php
/**
 * Writes Elementor-importable JSON for every page, saved section, and the
 * header/footer templates, plus a colour/typography summary.
 *
 * Run with: wp eval-file export_templates.php
 */

$out = '/var/lib/freelancer/projects/40717325/deliverable/elementor-templates';
if ( ! is_dir( $out ) ) {
	mkdir( $out, 0755, true );
}

/**
 * Elementor's template-import format. `type` decides where it lands:
 * 'page' imports as a full page, 'container' as a reusable section.
 */
function ug_export( $post_id, $type, $file, $dir ) {
	$data = get_post_meta( $post_id, '_elementor_data', true );
	if ( empty( $data ) ) {
		WP_CLI::warning( "no Elementor data on #$post_id" );
		return false;
	}

	$payload = [
		'version'       => '0.4',
		'title'         => get_the_title( $post_id ),
		'type'          => $type,
		'content'       => json_decode( $data, true ),
		'page_settings' => (object) [],
	];

	file_put_contents(
		"$dir/$file.json",
		wp_json_encode( $payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES )
	);
	return true;
}

$count = 0;

foreach ( [ 'home', 'play', 'design', 'about', 'contact',
            'scorecard', 'useful', 'disclaimer' ] as $slug ) {
	$p = get_posts( [ 'post_type' => 'page', 'name' => $slug, 'numberposts' => 1 ] );
	if ( $p && ug_export( $p[0]->ID, 'page', "page-$slug", $out ) ) {
		$count++;
	}
}

foreach ( get_posts( [ 'post_type' => 'elementor_library', 'numberposts' => -1 ] ) as $t ) {
	// The active kit is also an elementor_library post but holds settings, not
	// a layout — exporting it as a section would produce an empty template.
	if ( 'kit' === get_post_meta( $t->ID, '_elementor_template_type', true ) ) {
		continue;
	}
	if ( ug_export( $t->ID, 'container', 'section-' . $t->post_name, $out ) ) {
		$count++;
	}
}

foreach ( get_posts( [ 'post_type' => 'elementor-hf', 'numberposts' => -1 ] ) as $t ) {
	if ( ug_export( $t->ID, 'container', $t->post_name, $out ) ) {
		$count++;
	}
}

// The global palette and fonts, in a form that is readable without WordPress.
$kit_id  = (int) get_option( 'elementor_active_kit' );
$kit     = get_post_meta( $kit_id, '_elementor_page_settings', true );
$summary = [
	'system_colors'     => $kit['system_colors'] ?? [],
	'custom_colors'     => $kit['custom_colors'] ?? [],
	'system_typography' => $kit['system_typography'] ?? [],
	'container_width'   => $kit['container_width'] ?? null,
	'note'              => 'These are placeholder values. Replace the five HEX codes in '
	                     . 'Elementor > Site Settings > Global Colors and every section '
	                     . 'updates, because no colour is hard-coded in the layouts.',
];
file_put_contents(
	"$out/global-styles.json",
	wp_json_encode( $summary, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES )
);

WP_CLI::success( "$count templates exported to $out" );
