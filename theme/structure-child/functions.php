<?php
/**
 * Structure Template — Hello Elementor child theme.
 *
 * @package structure-child
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Load the parent stylesheet first, then this one.
 */
function structure_child_enqueue_styles() {
	wp_enqueue_style(
		'hello-elementor-parent',
		get_template_directory_uri() . '/style.css',
		[],
		wp_get_theme( 'hello-elementor' )->get( 'Version' )
	);

	wp_enqueue_style(
		'structure-child',
		get_stylesheet_uri(),
		[ 'hello-elementor-parent' ],
		wp_get_theme()->get( 'Version' )
	);
}
add_action( 'wp_enqueue_scripts', 'structure_child_enqueue_styles', 20 );

/**
 * Elementor ships the styling for angled section dividers in a conditional
 * stylesheet ('e-shapes') that it only enqueues from the asset list it writes
 * while saving a document in the editor. This build's layouts are generated, so
 * that list can be missing and the divider SVGs then render unpositioned, at
 * their intrinsic size — which overflows the viewport on small screens.
 * The dividers are structural here, so load the stylesheet unconditionally.
 */
function structure_child_shape_dividers() {
	if ( ! defined( 'ELEMENTOR_VERSION' ) ) {
		return;
	}

	if ( ! wp_style_is( 'e-shapes', 'registered' ) ) {
		wp_register_style(
			'e-shapes',
			ELEMENTOR_ASSETS_URL . 'css/conditionals/shapes.min.css',
			[],
			ELEMENTOR_VERSION
		);
	}

	wp_enqueue_style( 'e-shapes' );
}
add_action( 'wp_enqueue_scripts', 'structure_child_shape_dividers', 30 );

/**
 * Register the menu location used by the header template.
 */
function structure_child_menus() {
	register_nav_menus( [
		'menu-1' => __( 'Primary', 'structure-child' ),
		'footer' => __( 'Footer', 'structure-child' ),
	] );
}
add_action( 'after_setup_theme', 'structure_child_menus' );
